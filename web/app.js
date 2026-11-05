'use strict';

const $ = id => document.getElementById(id);
const state = { data: null, mode: 'confirmed', loading: false };
const romeDay = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Rome' });
const fullDate = new Intl.DateTimeFormat('it-IT', { timeZone: 'Europe/Rome', weekday: 'long', day: 'numeric', month: 'long' });
const timestamp = new Intl.DateTimeFormat('it-IT', { timeZone: 'Europe/Rome', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
const today = () => romeDay.format(new Date());
const SMALL_TITLE_WORDS = new Set(['a', 'ad', 'al', 'all', 'alla', 'alle', 'agli', 'con', 'da', 'dai', 'dal', 'dalla', 'dalle', 'dagli', 'de', 'dei', 'del', 'della', 'delle', 'degli', 'di', 'e', 'ed', 'fra', 'gli', 'i', 'il', 'in', 'la', 'le', 'lo', 'ne', 'negli', 'nei', 'nel', 'nella', 'nelle', 'o', 'per', 'su', 'sul', 'sulla', 'tra', 'un', 'una', 'uno', 'and', 'in', 'of', 'on', 'the', 'to']);
let canonicalTitles = new Map();

function titleKey(value) {
  return String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('it').replace(/[^a-z0-9]+/g, ' ').trim();
}

function titleCase(value) {
  let word = 0;
  return String(value).toLocaleLowerCase('it').split(/(\s+)/).map(token => {
    if (!token) return token;
    const bare = token.replace(/[^\p{L}]/gu, '');
    if (!bare) return token;
    const capitalize = word === 0 || !SMALL_TITLE_WORDS.has(bare);
    word += 1;
    if (!capitalize) return token;
    return token.replace(/(^|['’])(\p{L})/gu, (match, prefix, letter) => prefix + letter.toLocaleUpperCase('it'));
  }).join('');
}

function shouty(value) {
  const letters = String(value).match(/\p{L}/gu) || [];
  if (!letters.length) return false;
  const upper = letters.filter(letter => letter === letter.toLocaleUpperCase('it') && letter !== letter.toLocaleLowerCase('it')).length;
  return upper / letters.length >= 0.6;
}

function indexTitles(rows) {
  const groups = new Map();
  for (const row of rows) {
    if (!row || typeof row.title !== 'string') continue;
    const key = titleKey(row.title);
    if (!key) continue;
    const group = groups.get(key) || new Map();
    group.set(row.title, (group.get(row.title) || 0) + 1);
    groups.set(key, group);
  }
  const titles = new Map();
  for (const [key, group] of groups) {
    const variants = [...group.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], 'it'));
    const normal = variants.find(([variant]) => !shouty(variant));
    titles.set(key, normal ? normal[0] : titleCase(variants[0][0]));
  }
  canonicalTitles = titles;
}

function displayTitle(value) {
  return canonicalTitles.get(titleKey(value)) || String(value);
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function safeUrl(value) {
  try {
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) ? url.href : null;
  } catch { return null; }
}

function link(text, url, className) {
  const href = safeUrl(url);
  if (!href) return null;
  const anchor = element('a', className, text);
  anchor.href = href;
  anchor.target = '_blank';
  anchor.rel = 'noopener noreferrer';
  return anchor;
}

function dateLabel(value) {
  const date = new Date(`${value}T12:00:00+01:00`);
  return Number.isNaN(date.valueOf()) ? value : fullDate.format(date);
}

function driveInRange(value) {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 30;
}

function screeningValid(item) {
  return item && typeof item.title === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(item.date || '') && /^\d{2}:\d{2}$/.test(item.time || '') && ['original', 'italian', 'unknown', 'dubbed'].includes(item.classification);
}

function availableRows() {
  const now = new Date();
  const currentDay = today();
  const currentTime = new Intl.DateTimeFormat('it-IT', { timeZone: 'Europe/Rome', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).format(now);
  return (state.data?.screenings || []).filter(screeningValid).filter(item => item.classification !== 'dubbed' && (item.date > currentDay || (item.date === currentDay && item.time >= currentTime)) && driveInRange(item.driveMinutes));
}

function setOptions(id, pairs, initial) {
  const select = $(id);
  const selected = select.value;
  select.replaceChildren(new Option(initial, ''));
  pairs.forEach(([value, label]) => select.add(new Option(label, value)));
  if (pairs.some(([value]) => value === selected)) select.value = selected;
}

function updateOptions() {
  const rows = availableRows();
  const dates = [...new Set(rows.map(item => item.date))].sort();
  const cinemas = [...new Map(rows.map(item => [String(item.cinemaId || item.cinema), item.cinema])).entries()].sort((a, b) => a[1].localeCompare(b[1], 'it'));
  setOptions('date', dates.map(value => [value, dateLabel(value)]), 'Tutte le date');
  setOptions('cinema', cinemas, 'Tutti i cinema');
}

function filterRows() {
  const query = $('search').value.trim().toLocaleLowerCase('it');
  return availableRows().filter(item => (!$('date').value || item.date === $('date').value) && (!$('cinema').value || String(item.cinemaId || item.cinema) === $('cinema').value) && (!query || item.title.toLocaleLowerCase('it').includes(query)) && ($('include-italian').checked || item.classification !== 'italian'));
}

function showNotice(title, message, retry = false) {
  const notice = element('div', 'notice');
  notice.append(element('h2', '', title), element('p', '', message));
  if (retry) {
    const button = element('button', 'primary', 'Riprova adesso');
    button.type = 'button';
    button.addEventListener('click', () => load(true));
    notice.append(button);
  }
  $('results').replaceChildren(notice);
}

function rowCard(item) {
  const article = element('article', 'screening');
  const time = element('time', 'screening-time', item.time);
  time.dateTime = `${item.date}T${item.time}`;
  const info = element('div', 'screening-info');
  info.append(element('h3', '', displayTitle(item.title)));
  const badges = element('div', 'badges');
  const badgeText = item.classification === 'italian' ? 'ORIGINALE ITALIANO' : item.classification === 'unknown' ? 'LINGUA DA VERIFICARE' : 'VERSIONE ORIGINALE';
  badges.append(element('span', `badge${item.classification === 'unknown' ? ' unknown' : ''}`, badgeText));
  if (item.language) badges.append(element('span', 'language', item.language));
  info.append(badges);
  if (item.evidence) info.append(element('p', 'evidence', item.evidence));
  const place = element('div', 'screening-place');
  place.append(element('p', 'place-name', item.cinema || 'Cinema'), element('p', 'place-meta', `${item.city || 'Pescara'} · circa ${item.driveMinutes} min in auto`));
  const actions = element('div', 'actions');
  const booking = link('Orari e biglietti ↗', item.bookingUrl || item.sourceUrl, 'ticket');
  if (booking) actions.append(booking);
  const source = link('Fonte', item.sourceUrl);
  if (source) actions.append(source);
  const destination = `${item.cinema || ''} ${item.city || 'Pescara'}`.trim();
  const directions = link('Indicazioni ↗', `https://www.google.com/maps/dir/?api=1&origin=Piazza+Salotto+Pescara&destination=${encodeURIComponent(destination)}&travelmode=driving`);
  if (directions) actions.append(directions);
  place.append(actions);
  article.append(time, info, place);
  return article;
}

function render() {
  if (!state.data) return;
  const filtered = filterRows();
  const confirmed = filtered.filter(item => item.classification === 'original' || item.classification === 'italian');
  const unknown = filtered.filter(item => item.classification === 'unknown');
  $('confirmed-count').textContent = confirmed.length;
  $('unknown-count').textContent = unknown.length;
  const rows = state.mode === 'confirmed' ? confirmed : unknown;
  rows.sort((a, b) => a.date.localeCompare(b.date) || a.time.localeCompare(b.time) || displayTitle(a.title).localeCompare(displayTitle(b.title), 'it'));
  $('result-count').textContent = `${rows.length} ${rows.length === 1 ? 'proiezione' : 'proiezioni'}`;
  $('confirmed-tab').classList.toggle('active', state.mode === 'confirmed');
  $('unknown-tab').classList.toggle('active', state.mode === 'unknown');
  $('confirmed-tab').setAttribute('aria-selected', String(state.mode === 'confirmed'));
  $('unknown-tab').setAttribute('aria-selected', String(state.mode === 'unknown'));
  $('mode-note').textContent = state.mode === 'confirmed' ? 'Solo proiezioni con indicazioni di lingua originale nella fonte. Sono incluse le versioni originali italiane.' : 'Queste proiezioni non hanno una conferma sufficiente sulla lingua: potrebbero essere doppiate. Controlla la fonte prima di prenotare.';
  if (!rows.length) {
    const filtersActive = $('search').value.trim() || $('date').value || $('cinema').value || !$('include-italian').checked;
    const unavailable = state.data.sources.some(source => source.status !== 'ok');
    const message = filtersActive ? 'Prova a cambiare data, cinema o titolo. Puoi anche aggiornare le programmazioni.' : state.mode === 'unknown' ? 'Non risultano altre proiezioni da verificare nelle fonti consultate.' : unavailable ? 'Nessuna proiezione confermata nelle fonti disponibili. Alcuni cinema richiedono una verifica diretta: controlla lo stato delle fonti qui sotto.' : 'Nelle programmazioni consultate non risultano proiezioni con lingua originale confermata. Gli orari possono essere aggiunti durante la settimana.';
    showNotice(state.mode === 'unknown' ? 'Nessuna proiezione da verificare' : 'Nessuna proiezione confermata', message);
    return;
  }
  const fragment = document.createDocumentFragment();
  let previousDate = '';
  for (const item of rows) {
    if (item.date !== previousDate) {
      const heading = element('h2', 'day-heading', dateLabel(item.date));
      fragment.append(heading);
      previousDate = item.date;
    }
    fragment.append(rowCard(item));
  }
  $('results').replaceChildren(fragment);
}

function renderSources() {
  const sources = state.data.sources;
  const ok = sources.filter(source => source.status === 'ok').length;
  $('source-summary').textContent = `${ok} di ${sources.length} fonti disponibili`;
  const fragment = document.createDocumentFragment();
  for (const source of sources) {
    const article = element('article', 'source');
    const top = element('div', 'source-top');
    const status = source.status === 'ok' ? 'Consultata' : source.status === 'manual' ? 'Verifica sul sito' : 'Non disponibile';
    top.append(element('span', 'source-name', source.name || source.id), element('span', `source-status ${source.status === 'ok' ? '' : source.status === 'manual' ? 'manual' : 'error'}`, status));
    article.append(top);
    if (source.message) article.append(element('p', '', source.message));
    if (driveInRange(source.driveMinutes)) article.append(element('p', '', `Circa ${source.driveMinutes} minuti in auto dal centro`));
    const sourceLink = link('Apri la programmazione ↗', source.url);
    if (sourceLink) article.append(sourceLink);
    fragment.append(article);
  }
  $('sources').replaceChildren(fragment);
  $('notes').replaceChildren(...state.data.notes.map(note => element('p', '', note)));
}

async function load(refresh = false) {
  if (state.loading) return;
  state.loading = true;
  $('refresh').disabled = true;
  $('results').setAttribute('aria-busy', 'true');
  $('updated').textContent = 'Controllo le programmazioni…';
  const status = $('load-status');
  if (status) {
    status.textContent = 'Aggiorno gli orari dai cinema: può richiedere fino a un minuto.';
    status.hidden = !state.data;
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch(`/api/screenings${refresh ? '?refresh=1' : ''}`, { signal: controller.signal, cache: 'no-store' });
    if (!response.ok) throw new Error(`Il server ha risposto con errore ${response.status}.`);
    const data = await response.json();
    if (!Array.isArray(data.screenings) || !Array.isArray(data.sources)) throw new Error('La risposta delle programmazioni non è valida.');
    const notes = Array.isArray(data.notes) ? data.notes.filter(note => typeof note === 'string' && note.trim()) : [];
    state.data = { ...data, notes };
    indexTitles(data.screenings);
    updateOptions();
    render();
    renderSources();
    const updated = new Date(data.updatedAt);
    $('updated').textContent = Number.isNaN(updated.valueOf()) ? 'Programmazioni aggiornate' : `Controllato il ${timestamp.format(updated)}`;
  } catch (error) {
    $('updated').textContent = state.data ? 'Aggiornamento fallito · dati precedenti' : 'Collegamento non riuscito';
    if (state.data) {
      const notice = element('div', 'notice');
      notice.setAttribute('role', 'alert');
      notice.append(element('h2', '', 'Aggiornamento non riuscito'), element('p', '', 'Stai vedendo i dati dell’ultimo controllo. Premi Aggiorna per riprovare.'));
      render();
      $('results').prepend(notice);
    } else {
      showNotice('Non riesco a caricare gli orari', error.name === 'AbortError' ? 'I siti dei cinema stanno impiegando troppo tempo. Riprova tra un momento.' : `${error.message} Verifica la connessione e che il programma sia ancora aperto.`, true);
      $('source-summary').textContent = 'Fonti non ancora verificate';
    }
  } finally {
    clearTimeout(timeout);
    state.loading = false;
    $('refresh').disabled = false;
    $('results').setAttribute('aria-busy', 'false');
    if (status) status.hidden = true;
  }
}

$('search').addEventListener('input', render);
['date', 'cinema', 'include-italian'].forEach(id => $(id).addEventListener('change', render));
$('refresh').addEventListener('click', () => load(true));
$('confirmed-tab').addEventListener('click', () => { state.mode = 'confirmed'; render(); });
$('unknown-tab').addEventListener('click', () => { state.mode = 'unknown'; render(); });
load();
