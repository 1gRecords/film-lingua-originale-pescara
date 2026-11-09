'use strict';

const $ = id => document.getElementById(id);
const LANG_KEY = 'cinemavo.lang';
const MESSAGES = {
  it: {
    'document.title': 'Voci originali · Cinema a Pescara',
    'meta.description': 'Proiezioni in lingua originale a Pescara e dintorni. Orari, fonti e posizione dei cinema, senza film doppiati.',
    'nav.skip': 'Vai ai risultati',
    'masthead.radius': 'Entro circa 30 min in auto',
    'language.group': 'Lingua del sito',
    'intro.edition': 'Le voci sono quelle del film.',
    'app.title': 'Voci originali',
    'intro.description': 'Trova le proiezioni in lingua originale vicino a Pescara, compresi i film italiani. I film doppiati sono esclusi.',
    'refresh.button': 'Aggiorna gli orari',
    'updated.connecting': 'Collegamento alle programmazioni…',
    'updated.checking': 'Controllo le programmazioni…',
    'updated.checked': 'Controllato il {date}',
    'updated.ok': 'Programmazioni aggiornate',
    'updated.failedPrevious': 'Aggiornamento fallito · dati precedenti',
    'updated.failed': 'Collegamento non riuscito',
    'finder.label': 'Filtra le proiezioni',
    'search.label': 'Cerca un film',
    'search.placeholder': 'Titolo del film…',
    'date.label': 'Quando',
    'date.all': 'Tutte le date',
    'cinema.label': 'Dove',
    'cinema.all': 'Tutti i cinema',
    'italian.toggle': 'Includi gli originali italiani',
    'tabs.label': 'Affidabilità della lingua',
    'tab.confirmed': 'Lingua confermata',
    'tab.unknown': 'Da verificare',
    'results.label': 'Proiezioni',
    'results.one': '{count} proiezione',
    'results.many': '{count} proiezioni',
    'mode.confirmed': 'Qui trovi solo proiezioni con indicazioni di lingua originale nella fonte.',
    'mode.unknown': 'Queste proiezioni non hanno una conferma sufficiente sulla lingua: potrebbero essere doppiate. Controlla la fonte prima di prenotare.',
    'loading.title': 'Controllo i cinema vicini',
    'loading.body': 'Raccolgo gli orari disponibili e le indicazioni sulla lingua.',
    'load.updating': 'Aggiorno gli orari dai cinema: può richiedere fino a un minuto.',
    'error.title': 'Non riesco a caricare gli orari',
    'error.http': 'Il server ha risposto con errore {status}.',
    'error.invalid': 'La risposta delle programmazioni non è valida.',
    'error.timeout': 'I siti dei cinema stanno impiegando troppo tempo. Riprova tra un momento.',
    'error.connection': '{message} Verifica la connessione e che il programma sia ancora aperto.',
    'stale.title': 'Aggiornamento non riuscito',
    'stale.body': 'Stai vedendo i dati dell’ultimo controllo. Premi Aggiorna per riprovare.',
    'retry': 'Riprova adesso',
    'empty.confirmed.title': 'Nessuna proiezione confermata',
    'empty.unknown.title': 'Nessuna proiezione da verificare',
    'empty.filters': 'Prova a cambiare data, cinema o titolo. Puoi anche aggiornare le programmazioni.',
    'empty.unknown.body': 'Non risultano altre proiezioni da verificare nelle fonti consultate.',
    'empty.unavailable.body': 'Nessuna proiezione confermata nelle fonti disponibili. Alcuni cinema richiedono una verifica diretta: controlla lo stato delle fonti qui sotto.',
    'empty.none.body': 'Nelle programmazioni consultate non risultano proiezioni con lingua originale confermata. Gli orari possono essere aggiunti durante la settimana.',
    'badge.original': 'VERSIONE ORIGINALE',
    'badge.italian': 'ORIGINALE ITALIANO',
    'badge.unknown': 'LINGUA DA VERIFICARE',
    'place.meta': '{city}',
    'place.defaultCinema': 'Cinema',
    'place.defaultCity': 'Pescara',
    'actions.tickets': 'Orari e biglietti ↗',
    'actions.source': 'Fonte',
    'actions.location': 'Posizione ↗',
    'sources.updating': 'In aggiornamento',
    'sources.unverified': 'Fonti non ancora verificate',
    'sources.summary': '{ok} di {total} fonti disponibili',
    'source.status.ok': 'Consultata',
    'source.status.manual': 'Verifica sul sito',
    'source.status.error': 'Non disponibile',
    'source.open': 'Apri la programmazione ↗',
    'source.manual.cityplex': 'Il sito Cityplex elenca titoli, date e orari ma non la lingua per proiezione. Verificare la versione sul sito o in biglietteria.',
    'source.manual.generic': 'Il sito elenca titoli, date e orari ma non la lingua per proiezione. Verificare la versione sul sito o in biglietteria.',
    'source.manual.default': 'Verifica manuale sul sito ufficiale.',
    'source.ok': '{days}/{total} giorni letti',
    'source.error': '{days}/{total} giorni letti; {reason}',
    'coverage.title': 'Le fonti, senza sorprese.',
    'coverage.description': 'La lingua viene verificata sulle indicazioni delle singole proiezioni. Una produzione italiana, da sola, non prova che l’audio sia originale. Se un sito non risponde, lo trovi segnalato qui.',
    'notes.dev': 'VERSIONE DI SVILUPPO: Massimo e Sant’Andrea richiedono verifica manuale.',
    'notes.drive': 'Tempi di guida stimati dal centro di Pescara; non sono misure del traffico attuale.',
    'notes.sevenDays': 'Sette giorni di programmazione; la nazionalità italiana non dimostra la lingua originale.',
    'footer.about': 'Pescara e dintorni · Nessun account, nessuna installazione di pacchetti.',
    'footer.times': 'Controlla lingua e orario sul sito del cinema prima di partire.',
    'footer.tmdb': 'Questo prodotto usa l’API di TMDB ma non è approvato o certificato da TMDB.',
    'tmdb.rating': 'TMDB {rating}/10 · {votes} voti',
    'tmdb.plotFallback': 'Trama non disponibile in italiano: mostro quella inglese.',
    'tmdb.plotMissing': 'Trama non disponibile.',
    'language.italian': 'Italiano',
    'language.dubbed': 'Doppiato',
    'language.original': 'Versione originale',
    'language.unknown': 'Lingua da verificare',
    'language.it': 'Italiano',
    'language.en': 'Inglese',
    'language.fr': 'Francese',
    'language.es': 'Spagnolo',
    'language.de': 'Tedesco',
    'language.ko': 'Coreano',
    'language.ja': 'Giapponese',
    'language.ru': 'Russo',
    'language.pt': 'Portoghese',
    'language.zh': 'Cinese',
    'evidence.dubbed.label': 'La fonte indica una versione doppiata{labelSuffix}',
    'evidence.dubbed.audio': 'Film in {filmLanguage}; la proiezione è in {audioLanguage}: versione doppiata.',
    'evidence.italian.metadata': '{sourceEvidence}{yearNote}',
    'evidence.original.verified': 'Lingua originale verificata ({filmLanguage}) e audio della proiezione coerente.{yearNote}',
    'evidence.original.label': 'Indicazione esplicita nella fonte: {label}',
    'evidence.original.title': 'Il titolo indica la versione originale: {title}',
    'evidence.unknown.audio': 'Audio indicato dalla fonte: {audioLanguage}; lingua originale non verificata.',
    'evidence.unknown.none': 'Nessuna indicazione esplicita di versione originale',
    'evidence.yearNote': ' (anno non disponibile)',
    'evidence.dailyNote': ' (nota della scheda giornaliera, valida per tutti gli orari della stessa scheda).'
  },
  en: {
    'document.title': 'Original voices · Cinema in Pescara',
    'meta.description': 'Original-language screenings in and around Pescara. Showtimes, sources and cinema locations, without dubbed films.',
    'nav.skip': 'Skip to results',
    'masthead.radius': 'Within about 30 min by car',
    'language.group': 'Site language',
    'intro.edition': 'The voices are the film’s own.',
    'app.title': 'Original voices',
    'intro.description': 'Find original-language screenings near Pescara, including Italian films. Dubbed screenings are excluded.',
    'refresh.button': 'Refresh showtimes',
    'updated.connecting': 'Connecting to showtimes…',
    'updated.checking': 'Checking showtimes…',
    'updated.checked': 'Updated {date}',
    'updated.ok': 'Showtimes updated',
    'updated.failedPrevious': 'Update failed · showing previous data',
    'updated.failed': 'Connection failed',
    'finder.label': 'Filter screenings',
    'search.label': 'Search for a film',
    'search.placeholder': 'Film title…',
    'date.label': 'When',
    'date.all': 'All dates',
    'cinema.label': 'Where',
    'cinema.all': 'All cinemas',
    'italian.toggle': 'Include Italian originals',
    'tabs.label': 'Language confidence',
    'tab.confirmed': 'Language confirmed',
    'tab.unknown': 'To verify',
    'results.label': 'Screenings',
    'results.one': '{count} screening',
    'results.many': '{count} screenings',
    'mode.confirmed': 'Only screenings with an original-language indication in the source appear here.',
    'mode.unknown': 'These screenings do not have enough language evidence: they may be dubbed. Check the source before booking.',
    'loading.title': 'Checking nearby cinemas',
    'loading.body': 'Collecting available showtimes and language indications.',
    'load.updating': 'Updating showtimes from the cinemas: this can take up to a minute.',
    'error.title': 'I can’t load the showtimes',
    'error.http': 'The server returned error {status}.',
    'error.invalid': 'The showtimes response is not valid.',
    'error.timeout': 'The cinema sites are taking too long. Try again in a moment.',
    'error.connection': '{message} Check your connection and that the app is still running.',
    'stale.title': 'Update failed',
    'stale.body': 'You are seeing data from the last check. Press Refresh to try again.',
    'retry': 'Try again',
    'empty.confirmed.title': 'No confirmed screenings',
    'empty.unknown.title': 'No screenings to verify',
    'empty.filters': 'Try changing the date, cinema or title. You can also refresh the showtimes.',
    'empty.unknown.body': 'The sources checked list no other screenings to verify.',
    'empty.unavailable.body': 'No confirmed screenings in the available sources. Some cinemas need a direct check: see the source status below.',
    'empty.none.body': 'The schedules checked list no screenings with a confirmed original language. Showtimes can be added during the week.',
    'badge.original': 'ORIGINAL VERSION',
    'badge.italian': 'ITALIAN ORIGINAL',
    'badge.unknown': 'LANGUAGE TO VERIFY',
    'place.meta': '{city}',
    'place.defaultCinema': 'Cinema',
    'place.defaultCity': 'Pescara',
    'actions.tickets': 'Times and tickets ↗',
    'actions.source': 'Source',
    'actions.location': 'Location ↗',
    'sources.updating': 'Updating',
    'sources.unverified': 'Sources not checked yet',
    'sources.summary': '{ok} of {total} sources available',
    'source.status.ok': 'Checked',
    'source.status.manual': 'Check the site',
    'source.status.error': 'Unavailable',
    'source.open': 'Open the schedule ↗',
    'source.manual.cityplex': 'The Cityplex site lists titles, dates and times but not the language for each screening. Check the version on the site or at the box office.',
    'source.manual.generic': 'The site lists titles, dates and times but not the language for each screening. Check the version on the site or at the box office.',
    'source.manual.default': 'Manual check on the official site.',
    'source.ok': '{days}/{total} days read',
    'source.error': '{days}/{total} days read; {reason}',
    'coverage.title': 'The sources, no surprises.',
    'coverage.description': 'Language is checked against each screening’s own indication. An Italian production alone does not prove the audio is original. If a site does not respond, it is flagged here.',
    'notes.dev': 'DEVELOPMENT VERSION: Massimo and Sant’Andrea need a manual check.',
    'notes.drive': 'Driving times are estimates from central Pescara; they are not live traffic measurements.',
    'notes.sevenDays': 'Seven days of showtimes; Italian nationality alone does not prove the original language.',
    'footer.about': 'Pescara and surroundings · No account, no package installation.',
    'footer.times': 'Check language and time on the cinema site before you leave.',
    'footer.tmdb': 'This product uses the TMDB API but is not endorsed or certified by TMDB.',
    'tmdb.rating': 'TMDB {rating}/10 · {votes} votes',
    'tmdb.plotFallback': 'Plot not available in Italian; showing the English one.',
    'tmdb.plotMissing': 'Plot not available.',
    'language.italian': 'Italian',
    'language.dubbed': 'Dubbed',
    'language.original': 'Original version',
    'language.unknown': 'Language to verify',
    'language.it': 'Italian',
    'language.en': 'English',
    'language.fr': 'French',
    'language.es': 'Spanish',
    'language.de': 'German',
    'language.ko': 'Korean',
    'language.ja': 'Japanese',
    'language.ru': 'Russian',
    'language.pt': 'Portuguese',
    'language.zh': 'Chinese',
    'evidence.dubbed.label': 'The source marks a dubbed version.',
    'evidence.dubbed.audio': 'Film language: {filmLanguage}; screening audio: {audioLanguage}. This is a dubbed version.',
    'evidence.italian.metadata': 'Curated metadata confirms Italian as the original language{yearNote}.',
    'evidence.original.verified': 'Verified original language ({filmLanguage}) and the screening audio matches.{yearNote}',
    'evidence.original.label': 'Explicit original-version indication in the source.',
    'evidence.original.title': 'The title says original version: {title}',
    'evidence.unknown.audio': 'Audio listed by the source: {audioLanguage}; original language not verified.',
    'evidence.unknown.none': 'No explicit original-version indication.',
    'evidence.yearNote': ' (year unavailable)',
    'evidence.dailyNote': ' (daily listing note, valid for every time in that listing).'
  }
};

function readLang() {
  try {
    const value = localStorage.getItem(LANG_KEY);
    return value === 'en' || value === 'it' ? value : 'it';
  } catch {
    return 'it';
  }
}

function saveLang(value) {
  try {
    localStorage.setItem(LANG_KEY, value);
  } catch {
    // Storage can be blocked; the switch still works for this page.
  }
}

function t(key, params) {
  const value = MESSAGES[state.lang]?.[key];
  if (value === undefined) return key;
  if (!params) return value;
  return value.replace(/\{(\w+)\}/g, (match, name) => params[name] === undefined ? '' : String(params[name]));
}

function locale() {
  return state.lang === 'en' ? 'en-GB' : 'it-IT';
}

const state = { data: null, mode: 'confirmed', loading: false, lang: readLang() };
const romeDay = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Rome' });
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

function tmdbFilm(item) {
  const films = state.data?.tmdb?.films;
  if (!films || typeof films !== 'object' || typeof item.tmdbKey !== 'string') return null;
  const film = films[item.tmdbKey];
  return film && typeof film === 'object' ? film : null;
}

function tmdbBlock(item) {
  const film = tmdbFilm(item);
  if (!film) return null;
  const block = element('div', 'tmdb');
  const rating = typeof film.rating === 'number' && Number.isFinite(film.rating) ? film.rating : null;
  const votes = typeof film.votes === 'number' && Number.isFinite(film.votes) ? film.votes : 0;
  if (rating !== null) {
    block.append(element('p', 'tmdb-rating', t('tmdb.rating', {
      rating: rating.toFixed(1),
      votes: new Intl.NumberFormat(locale()).format(votes)
    })));
  }
  const italian = typeof film.overviewIt === 'string' ? film.overviewIt.trim() : '';
  const english = typeof film.overviewEn === 'string' ? film.overviewEn.trim() : '';
  let plot = state.lang === 'en' ? english : italian;
  let fallback = false;
  if (!plot && state.lang === 'it' && english) {
    plot = english;
    fallback = true;
  }
  if (plot) {
    block.append(element('p', 'tmdb-plot', plot));
    if (fallback) block.append(element('p', 'tmdb-note', t('tmdb.plotFallback')));
  } else if (rating !== null) {
    block.append(element('p', 'tmdb-note', t('tmdb.plotMissing')));
  }
  return block.childNodes.length ? block : null;
}

function dateLabel(value) {
  const date = new Date(`${value}T12:00:00+01:00`);
  if (Number.isNaN(date.valueOf())) return value;
  return new Intl.DateTimeFormat(locale(), { timeZone: 'Europe/Rome', weekday: 'long', day: 'numeric', month: 'long' }).format(date);
}

function timestampLabel(date) {
  return new Intl.DateTimeFormat(locale(), { timeZone: 'Europe/Rome', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }).format(date);
}

function languageName(code) {
  return t(`language.${String(code || '').toLowerCase()}`);
}

function languageLabel(item) {
  const code = typeof item.languageCode === 'string' ? item.languageCode : '';
  if (code) {
    const translated = t(code);
    if (translated !== code) return translated;
  }
  if (item.classification === 'italian') return t('language.italian');
  if (item.classification === 'unknown') return t('language.unknown');
  if (item.classification === 'dubbed') return t('language.dubbed');
  if (item.classification === 'original') return t('language.original');
  return state.lang === 'it' ? String(item.language || '') : '';
}

function evidenceText(item) {
  const params = item.evidenceParams && typeof item.evidenceParams === 'object' ? item.evidenceParams : {};
  const yearNote = params.titleOnly ? t('evidence.yearNote') : '';
  const dailyNote = params.dailyNote ? t('evidence.dailyNote') : '';
  let value;
  switch (item.evidenceCode) {
    case 'evidence.dubbed.label':
      value = t('evidence.dubbed.label', { labelSuffix: params.label ? `: ${params.label}` : '' });
      break;
    case 'evidence.dubbed.audio':
      value = t('evidence.dubbed.audio', {
        filmLanguage: languageName(params.filmLanguage),
        audioLanguage: languageName(params.audioLanguage)
      });
      break;
    case 'evidence.italian.metadata':
      value = t('evidence.italian.metadata', {
        sourceEvidence: String(params.sourceEvidence || ''),
        yearNote
      });
      break;
    case 'evidence.original.verified':
      value = t('evidence.original.verified', {
        filmLanguage: languageName(params.language),
        yearNote
      });
      break;
    case 'evidence.original.label':
      value = t('evidence.original.label', { label: String(params.label || '') });
      break;
    case 'evidence.original.title':
      value = t('evidence.original.title', { title: String(params.title || '') });
      break;
    case 'evidence.unknown.audio':
      value = t('evidence.unknown.audio', { audioLanguage: languageName(params.language) });
      break;
    case 'evidence.unknown.none':
      value = t('evidence.unknown.none');
      break;
    default:
      return state.lang === 'it' && typeof item.evidence === 'string' ? item.evidence : '';
  }
  return `${value}${dailyNote}`.trim();
}

function sourceMessage(source) {
  const params = source.messageParams && typeof source.messageParams === 'object' ? source.messageParams : {};
  if (typeof source.messageCode === 'string' && source.messageCode) {
    const translated = t(source.messageCode, {
      days: params.days,
      total: params.total,
      reason: params.reason
    });
    if (translated !== source.messageCode) return translated;
  }
  return state.lang === 'it' ? String(source.message || '') : '';
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
  const cinemas = [...new Map(rows.map(item => [String(item.cinemaId || item.cinema), item.cinema])).entries()].sort((a, b) => a[1].localeCompare(b[1], locale()));
  setOptions('date', dates.map(value => [value, dateLabel(value)]), t('date.all'));
  setOptions('cinema', cinemas, t('cinema.all'));
}

function filterRows() {
  const query = $('search').value.trim().toLocaleLowerCase(locale());
  return availableRows().filter(item => (!$('date').value || item.date === $('date').value) && (!$('cinema').value || String(item.cinemaId || item.cinema) === $('cinema').value) && (!query || item.title.toLocaleLowerCase(locale()).includes(query)) && ($('include-italian').checked || item.classification !== 'italian'));
}

function showNotice(title, message, retry = false) {
  const notice = element('div', 'notice');
  notice.append(element('h2', '', title), element('p', '', message));
  if (retry) {
    const button = element('button', 'primary', t('retry'));
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
  const badgeKey = item.classification === 'italian' ? 'badge.italian' : item.classification === 'unknown' ? 'badge.unknown' : 'badge.original';
  badges.append(element('span', `badge${item.classification === 'unknown' ? ' unknown' : ''}`, t(badgeKey)));
  const language = languageLabel(item);
  if (language) badges.append(element('span', 'language', language));
  info.append(badges);
  const evidence = evidenceText(item);
  if (evidence) info.append(element('p', 'evidence', evidence));
  const extra = tmdbBlock(item);
  if (extra) info.append(extra);
  const place = element('div', 'screening-place');
  place.append(element('p', 'place-name', item.cinema || t('place.defaultCinema')), element('p', 'place-meta', t('place.meta', { city: item.city || t('place.defaultCity') })));
  const actions = element('div', 'actions');
  const booking = link(t('actions.tickets'), item.bookingUrl || item.sourceUrl, 'ticket');
  if (booking) actions.append(booking);
  const source = link(t('actions.source'), item.sourceUrl);
  if (source) actions.append(source);
  const destination = `${item.cinema || ''} ${item.city || 'Pescara'}`.trim();
  const location = link(t('actions.location'), `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(destination)}`);
  if (location) actions.append(location);
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
  rows.sort((a, b) => a.date.localeCompare(b.date) || a.time.localeCompare(b.time) || displayTitle(a.title).localeCompare(displayTitle(b.title), locale()));
  $('result-count').textContent = t(rows.length === 1 ? 'results.one' : 'results.many', { count: rows.length });
  $('confirmed-tab').classList.toggle('active', state.mode === 'confirmed');
  $('unknown-tab').classList.toggle('active', state.mode === 'unknown');
  $('confirmed-tab').setAttribute('aria-selected', String(state.mode === 'confirmed'));
  $('unknown-tab').setAttribute('aria-selected', String(state.mode === 'unknown'));
  $('mode-note').textContent = state.mode === 'confirmed' ? t('mode.confirmed') : t('mode.unknown');
  if (!rows.length) {
    const filtersActive = $('search').value.trim() || $('date').value || $('cinema').value || !$('include-italian').checked;
    const unavailable = state.data.sources.some(source => source.status !== 'ok');
    const title = state.mode === 'unknown' ? t('empty.unknown.title') : t('empty.confirmed.title');
    const message = filtersActive ? t('empty.filters') : state.mode === 'unknown' ? t('empty.unknown.body') : unavailable ? t('empty.unavailable.body') : t('empty.none.body');
    showNotice(title, message);
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
  $('source-summary').textContent = t('sources.summary', { ok, total: sources.length });
  const fragment = document.createDocumentFragment();
  for (const source of sources) {
    const article = element('article', 'source');
    const top = element('div', 'source-top');
    const statusKey = source.status === 'ok' ? 'source.status.ok' : source.status === 'manual' ? 'source.status.manual' : 'source.status.error';
    top.append(element('span', 'source-name', source.name || source.id), element('span', `source-status ${source.status === 'ok' ? '' : source.status === 'manual' ? 'manual' : 'error'}`, t(statusKey)));
    article.append(top);
    const message = sourceMessage(source);
    if (message) article.append(element('p', '', message));
    const sourceLink = link(t('source.open'), source.url);
    if (sourceLink) article.append(sourceLink);
    fragment.append(article);
  }
  $('sources').replaceChildren(fragment);
  const codes = state.data.noteCodes || [];
  const notes = state.data.notes.map((note, index) => {
    const code = typeof codes[index] === 'string' ? codes[index] : '';
    const value = code ? t(code) : state.lang === 'it' ? note : '';
    return value ? element('p', '', value) : null;
  }).filter(Boolean);
  $('notes').replaceChildren(...notes);
}

function updateUpdatedLabel() {
  if (!state.data) return;
  const updated = new Date(state.data.updatedAt);
  $('updated').textContent = Number.isNaN(updated.valueOf()) ? t('updated.ok') : t('updated.checked', { date: timestampLabel(updated) });
}

function refreshLiveLabels() {
  if (state.loading) {
    $('updated').textContent = t('updated.checking');
    const status = $('load-status');
    if (status && !status.hidden) status.textContent = t('load.updating');
  } else if (state.data) {
    updateUpdatedLabel();
  } else {
    $('updated').textContent = t('updated.connecting');
    $('source-summary').textContent = t('sources.updating');
  }
}

function updateSwitch() {
  for (const button of document.querySelectorAll('.lang-option')) {
    button.setAttribute('aria-pressed', String(button.dataset.lang === state.lang));
  }
}

function applyStatic() {
  document.documentElement.lang = state.lang;
  document.title = t('document.title');
  for (const node of document.querySelectorAll('[data-i18n]')) node.textContent = t(node.dataset.i18n);
  for (const node of document.querySelectorAll('[data-i18n-placeholder]')) node.setAttribute('placeholder', t(node.dataset.i18nPlaceholder));
  for (const node of document.querySelectorAll('[data-i18n-aria-label]')) node.setAttribute('aria-label', t(node.dataset.i18nAriaLabel));
  for (const node of document.querySelectorAll('[data-i18n-content]')) node.setAttribute('content', t(node.dataset.i18nContent));
  updateSwitch();
}

function setLang(lang) {
  if (lang !== 'it' && lang !== 'en') return;
  if (lang !== state.lang) {
    state.lang = lang;
    saveLang(lang);
    applyStatic();
    if (state.data) {
      updateOptions();
      render();
      renderSources();
    }
  }
  refreshLiveLabels();
}

async function load(refresh = false) {
  if (state.loading) return;
  state.loading = true;
  $('refresh').disabled = true;
  $('results').setAttribute('aria-busy', 'true');
  $('updated').textContent = t('updated.checking');
  const status = $('load-status');
  if (status) {
    status.textContent = t('load.updating');
    status.hidden = !state.data;
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch(`/api/screenings${refresh ? '?refresh=1' : ''}`, { signal: controller.signal, cache: 'no-store' });
    if (!response.ok) throw new Error(t('error.http', { status: response.status }));
    const data = await response.json();
    if (!Array.isArray(data.screenings) || !Array.isArray(data.sources)) throw new Error(t('error.invalid'));
    const notes = Array.isArray(data.notes) ? data.notes.filter(note => typeof note === 'string' && note.trim()) : [];
    const noteCodes = Array.isArray(data.noteCodes) ? data.noteCodes.map(code => typeof code === 'string' ? code : '') : [];
    state.data = { ...data, notes, noteCodes };
    indexTitles(data.screenings);
    updateOptions();
    render();
    renderSources();
    updateUpdatedLabel();
  } catch (error) {
    $('updated').textContent = state.data ? t('updated.failedPrevious') : t('updated.failed');
    if (state.data) {
      const notice = element('div', 'notice');
      notice.setAttribute('role', 'alert');
      notice.append(element('h2', '', t('stale.title')), element('p', '', t('stale.body')));
      render();
      $('results').prepend(notice);
    } else {
      showNotice(t('error.title'), error.name === 'AbortError' ? t('error.timeout') : t('error.connection', { message: error.message }), true);
      $('source-summary').textContent = t('sources.unverified');
    }
  } finally {
    clearTimeout(timeout);
    state.loading = false;
    $('refresh').disabled = false;
    $('results').setAttribute('aria-busy', 'false');
    if (status) status.hidden = true;
  }
}

for (const button of document.querySelectorAll('.lang-option')) {
  button.addEventListener('click', () => setLang(button.dataset.lang));
}
$('search').addEventListener('input', render);
['date', 'cinema', 'include-italian'].forEach(id => $(id).addEventListener('change', render));
$('refresh').addEventListener('click', () => load(true));
$('confirmed-tab').addEventListener('click', () => { state.mode = 'confirmed'; render(); });
$('unknown-tab').addEventListener('click', () => { state.mode = 'unknown'; render(); });

applyStatic();
$('updated').textContent = t('updated.connecting');
$('source-summary').textContent = t('sources.updating');
load();
