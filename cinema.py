"""Draft live cinema finder. Standard library only; not yet tested end to end.
Run: python cinema.py --no-browser
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import html
import http.cookiejar
import json
from pathlib import Path
import re
import threading
import time
import unicodedata
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse, parse_qs
import webbrowser

import tmdb

ROOT = Path(__file__).resolve().parent
UCI_API = 'https://myuci---uci-backend-production-nfluwp7wga-oc.a.run.app/api'
SPACE_BASE = 'https://www.thespacecinema.it'
SPACE_PAGE = SPACE_BASE + '/cinema/montesilvano/al-cinema'
SPACE_API = SPACE_BASE + '/api/microservice/showings/cinemas/1026/films'
SPACE_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/131.0 Safari/537.36')
SOURCES = [
 {'id':'arca','name':"Multiplex L’Arca",'city':'Spoltore','driveMinutes':15,'url':'https://multicinema.it/Programmazione?cinema=arca'},
 {'id':'universo','name':'Multiplex Universo','city':'Silvi','driveMinutes':30,'url':'https://multicinema.it/Programmazione?cinema=universo'},
 {'id':'uci','name':'UCI Luxe Megalò','city':'Chieti','driveMinutes':30,'url':'https://www.ucicinemas.it/cinema/uci-cinemas-megalo/'},
 {'id':'massimo','name':'Cineteatro Massimo','city':'Pescara','driveMinutes':5,'url':'https://pescaracityplex.it/'},
 {'id':'santandrea','name':"Cineteatro Sant’Andrea",'city':'Pescara','driveMinutes':5,'url':'https://pescaracityplex.it/'},
 {'id':'space','name':'The Space Porto Allegro','city':'Montesilvano','driveMinutes':25,'url':SPACE_PAGE}]
CACHE = None
CACHE_AT = 0
CACHE_TTL = 600
TMDB_KEY_PATH = tmdb.KEY_PATH
LOCK = threading.Lock()
UCI_BASE = 'https://ucicinemas.it'
DAYS = 7
LANGUAGE_CODES = {
    'it': 'it', 'ita': 'it', 'italiano': 'it', 'italiana': 'it', 'italian': 'it',
    'en': 'en', 'eng': 'en', 'inglese': 'en', 'english': 'en',
    'fr': 'fr', 'fra': 'fr', 'fre': 'fr', 'francese': 'fr', 'french': 'fr',
    'es': 'es', 'spa': 'es', 'spagnolo': 'es', 'spagnola': 'es', 'spanish': 'es',
    'de': 'de', 'deu': 'de', 'ger': 'de', 'tedesco': 'de', 'tedesca': 'de', 'german': 'de',
    'ko': 'ko', 'kor': 'ko', 'coreano': 'ko', 'coreana': 'ko', 'korean': 'ko',
    'ja': 'ja', 'jpn': 'ja', 'giapponese': 'ja', 'japanese': 'ja',
    'ru': 'ru', 'rus': 'ru', 'russo': 'ru', 'russian': 'ru',
    'pt': 'pt', 'por': 'pt', 'portoghese': 'pt', 'portuguese': 'pt',
    'zh': 'zh', 'zho': 'zh', 'chi': 'zh', 'cinese': 'zh', 'chinese': 'zh',
}
LANGUAGE_NAMES = {
    'it': 'Italiano', 'en': 'Inglese', 'fr': 'Francese', 'es': 'Spagnolo',
    'de': 'Tedesco', 'ko': 'Coreano', 'ja': 'Giapponese', 'ru': 'Russo',
    'pt': 'Portoghese', 'zh': 'Cinese',
}
DUBBED_LABEL = re.compile(r'\bdoppiat[oaie]\b|\bdubbed\b')
ORIGINAL_LABEL = re.compile(
    r'versione originale|lingua originale|original version|'
    r'\b(?:v\.?o\.?s?\.?|o\.?v\.?|vos|vost|sott\.?\s*ita)\b')


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'CinemaVO/0.1 (personal local cinema finder)'})
    with urllib.request.urlopen(req, timeout=12) as response:
        data = response.read(3_000_001)
        if len(data) > 3_000_000:
            raise ValueError('Source response too large')
        return data.decode('utf-8', errors='replace')


class SpaceClient:
    """Cookie-session client for the official The Space JSON API.

    The lock keeps the seven daily requests one at a time and protects the
    shared opener. A failed cookie prime is reused for 60 seconds so one
    refresh does not retry it seven times.
    """

    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.lock = threading.Lock()
        self.primed = False
        self.prime_error = None
        self.prime_failed_at = 0.0

    def _get(self, url):
        request = urllib.request.Request(url, headers={'User-Agent': SPACE_UA})
        with self.opener.open(request, timeout=20) as response:
            return response.read(3_000_001)

    def _prime(self):
        try:
            self._get(SPACE_PAGE)
        except Exception as exc:
            self.primed = False
            self.prime_error = exc
            self.prime_failed_at = time.monotonic()
            raise
        self.primed = True
        self.prime_error = None

    def films(self, day):
        url = (f'{SPACE_API}?showingDate={day}T00:00:00&minEmbargoLevel=3'
               '&includesSession=true&includeSessionAttributes=true')
        with self.lock:
            if not self.primed:
                if self.prime_error is not None and time.monotonic() - self.prime_failed_at < 60:
                    raise self.prime_error
                self._prime()
            try:
                payload = self._get(url)
            except urllib.error.HTTPError as exc:
                if exc.code != 401:
                    raise
                self._prime()
                payload = self._get(url)
            if len(payload) > 3_000_000:
                raise ValueError('The Space: response too large')
            return json.loads(payload)


SPACE_CLIENT = SpaceClient()


def text(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', value))).strip()


def _last_sunday(year, month):
    last = date(year, month, 31)
    return (last - timedelta(days=(last.weekday() + 1) % 7)).day


def _rome_offset(moment):
    # EU DST switches at 01:00 UTC on the last Sunday of March and October.
    moment = moment.replace(tzinfo=timezone.utc) if moment.tzinfo is None else moment.astimezone(timezone.utc)
    start = datetime(moment.year, 3, _last_sunday(moment.year, 3), 1, tzinfo=timezone.utc)
    end = datetime(moment.year, 10, _last_sunday(moment.year, 10), 1, tzinfo=timezone.utc)
    return timezone(timedelta(hours=2)) if start <= moment < end else timezone(timedelta(hours=1))


def rome_now(utc=None):
    moment = utc or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(_rome_offset(moment))


def rome_today(utc=None):
    return rome_now(utc).date()


def normalize(value):
    decomposed = unicodedata.normalize('NFKD', str(value or ''))
    plain = ''.join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', plain.casefold())).strip()


def metadata():
    path = ROOT / 'language-overrides.json'
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return {}
    return raw if isinstance(raw, dict) else {}


def override_index(known):
    index = {}
    for key, entry in (known or {}).items():
        if not isinstance(entry, dict):
            continue
        title = str(entry.get('title') or key)
        normalized = normalize(title)
        if normalized:
            index.setdefault(normalized, []).append({**entry, 'title': title})
    return index


def match_override(title, year=None, known=None):
    candidates = override_index(known).get(normalize(title), [])
    if year is not None:
        return next((entry for entry in candidates if entry.get('year') == year), None)
    return candidates[0] if len(candidates) == 1 else None


def canonical_language(value):
    if not value:
        return ''
    token = text(str(value)).casefold().strip(' .')
    return LANGUAGE_CODES.get(token, token)


def classify_details(label, title='', known=None, audio_lang=None, year=None):
    """A nationality is never accepted as proof of original language."""
    label = text(label).casefold() if label else ''
    audio = canonical_language(audio_lang)
    audio_known = audio if audio in LANGUAGE_NAMES else ''
    entry = match_override(title, year, known)
    verified = canonical_language(entry.get('language')) if entry else ''
    verified_known = verified if verified in LANGUAGE_NAMES else ''
    verified_name = LANGUAGE_NAMES.get(verified, text(str(entry.get('language') or '')) if entry else '')
    title_only = bool(entry) and year is None
    year_note = ' (anno non disponibile)' if title_only else ''

    def details(classification, language, evidence, language_code, evidence_code, params):
        return {'classification': classification, 'language': language, 'evidence': evidence,
                'languageCode': language_code, 'evidenceCode': evidence_code,
                'evidenceParams': params}

    if DUBBED_LABEL.search(label):
        return details('dubbed', 'Doppiato',
                       'La fonte indica una versione doppiata' + (': ' + label if label else ''),
                       'language.dubbed', 'evidence.dubbed.label', {'label': label})
    if verified_known and audio_known and verified_known != audio_known:
        return details('dubbed', 'Doppiato',
                       f'Film in {verified_name}; la proiezione è in {LANGUAGE_NAMES[audio_known]}: versione doppiata.',
                       'language.dubbed', 'evidence.dubbed.audio',
                       {'filmLanguage': verified_known, 'audioLanguage': audio_known})
    if verified_known == 'it':
        evidence = text(str(entry.get('evidence') or 'Lingua originale italiana verificata'))
        return details('italian', 'Italiano', evidence + year_note,
                       'language.italian', 'evidence.italian.metadata',
                       {'sourceEvidence': evidence, 'titleOnly': title_only})
    if verified_known and audio_known and verified_known == audio_known:
        return details('original', verified_name,
                       f'Lingua originale verificata ({verified_name}) e audio della proiezione coerente.' + year_note,
                       'language.' + verified_known, 'evidence.original.verified',
                       {'language': verified_known, 'titleOnly': title_only})
    if ORIGINAL_LABEL.search(label):
        return details('original', 'Versione originale',
                       'Indicazione esplicita nella fonte: ' + label,
                       'language.original', 'evidence.original.label', {'label': label})
    if audio_known:
        return details('unknown', 'Lingua da verificare',
                       f'Audio indicato dalla fonte: {LANGUAGE_NAMES[audio_known]}; lingua originale non verificata.',
                       'language.unknown', 'evidence.unknown.audio', {'language': audio_known})
    return details('unknown', 'Lingua da verificare',
                   'Nessuna indicazione esplicita di versione originale',
                   'language.unknown', 'evidence.unknown.none', {})


def classify(label, title='', known=None, audio_lang=None, year=None):
    found = classify_details(label, title, known, audio_lang, year)
    return found['classification'], found['language'], found['evidence']


def http_url(value, fallback=''):
    if isinstance(value, str):
        candidate = value.strip()
        parsed = urlparse(candidate)
        if parsed.scheme in ('http', 'https') and parsed.netloc:
            return candidate
    return fallback


def screening(source, title, day, clock, label='', booking='', known=None,
              audio_lang=None, year=None, source_url=None):
    found = classify_details(label, title, known, audio_lang, year)
    key = '|'.join((source['id'], title, day, clock, found['classification']))
    link = http_url(source_url, '') or http_url(source.get('url'), '')
    return {'id':hashlib.sha1(key.encode()).hexdigest()[:16], 'title':title,
            'cinemaId':source['id'], 'cinema':source['name'], 'city':source['city'],
            'date':day, 'time':clock, 'language':found['language'],
            'classification':found['classification'], 'evidence':found['evidence'],
            'languageCode':found['languageCode'], 'evidenceCode':found['evidenceCode'],
            'evidenceParams':found['evidenceParams'], 'year':year,
            'sourceUrl':link,
            'bookingUrl':http_url(booking, link), 'driveMinutes':source['driveMinutes']}


def parse_multicinema(raw, source, day, known):
    rows = []
    # Bounding each block by the next item_small keeps the eventi/footer notes
    # from attaching to the last daily film.
    for block in re.split(r'(?=<div\s+class="item_small")', raw):
        opening = re.match(r'<div\s+class="item_small"[^>]*>', block)
        if not opening or 'getProgrammazioneGiornoSel()' not in opening.group(0):
            continue
        heading = re.search(r'<h3>\s*<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>\s*</h3>', block, re.S)
        if not heading:
            continue
        title = text(heading.group(2))
        if not title:
            continue
        times = re.search(r'<div class="tagcloud_orari">(.*?)</div>', block, re.S)
        if not times:
            continue
        notes = ' '.join(text(note) for note in re.findall(r'<span class="prog_nota\d">(.*?)</span>', block, re.S))
        language_note = bool(notes) and bool(DUBBED_LABEL.search(notes.casefold()) or ORIGINAL_LABEL.search(notes.casefold()))
        for h, m in re.findall(r'\b([0-2]?\d)[.:]([0-5]\d)\b', text(times.group(1))):
            if int(h) > 23:
                continue
            row = screening(source, title, day, f'{int(h):02}:{m}', notes,
                            urljoin(source['url'], html.unescape(heading.group(1))), known)
            if language_note:
                row['evidence'] += ' (nota della scheda giornaliera, valida per tutti gli orari della stessa scheda).'
                row['evidenceParams']['dailyNote'] = True
            rows.append(row)
    return rows


def load_multicinema(source, offset, known):
    day = (rome_today() + timedelta(days=offset)).isoformat()
    raw = fetch(source['url'] + '&giornoSettimana=' + str(offset))
    return parse_multicinema(raw, source, day, known)


def valid_clock(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{2}:\d{2}', value):
        return False
    hours, minutes = (int(part) for part in value.split(':'))
    return hours < 24 and minutes < 60


def parse_uci(payload, source, known):
    rows = []
    if not isinstance(payload, dict):
        return rows
    for movie in payload.get('data') or []:
        if not isinstance(movie, dict):
            continue
        title = text(str(movie.get('title') or ''))
        if not title:
            continue
        for screen in movie.get('screens') or []:
            if not isinstance(screen, dict):
                continue
            for versions in screen.values():
                if not isinstance(versions, list):
                    continue
                for version in versions:
                    if not isinstance(version, dict):
                        continue
                    language = version.get('language')
                    audio = str(language.get('slug') or language.get('name') or '') if isinstance(language, dict) else ''
                    subtitles = version.get('subtitles')
                    if isinstance(subtitles, dict):
                        subtitle = str(subtitles.get('name') or subtitles.get('slug') or '')
                    elif isinstance(subtitles, str):
                        subtitle = subtitles
                    else:
                        subtitle = ''
                    label = ' '.join(part for part in (audio, subtitle) if part)
                    for show in version.get('performances') or []:
                        if not isinstance(show, dict):
                            continue
                        day = show.get('day')
                        if not isinstance(day, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', day):
                            continue
                        clock = show.get('actual_start_at')
                        if not valid_clock(clock):
                            starts_at = show.get('starts_at')
                            clock = starts_at[11:16] if isinstance(starts_at, str) and len(starts_at) >= 16 else ''
                        if not valid_clock(clock):
                            continue
                        rows.append(screening(
                            source, title, day, clock, label,
                            urljoin(UCI_BASE, str(show.get('cart_link') or '')), known,
                            audio_lang=audio))
    return rows


def load_uci(source, offset, known):
    day = (rome_today() + timedelta(days=offset)).isoformat()
    return parse_uci(json.loads(fetch(UCI_API + '/theatres/uci-cinemas-megalo/programming/' + day)), source, known)


SPACE_ISO = re.compile(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})')


def space_start(session):
    for key in ('startTime', 'showTimeWithTimeZone'):
        value = session.get(key)
        match = SPACE_ISO.match(value) if isinstance(value, str) else None
        if not match:
            continue
        year, month, day, hours, minutes = match.groups()
        try:
            date.fromisoformat(f'{year}-{month}-{day}')
        except ValueError:
            continue
        clock = f'{hours}:{minutes}'
        if valid_clock(clock):
            return f'{year}-{month}-{day}', clock
    return '', ''


def space_year(film):
    value = film.get('releaseDate')
    if not isinstance(value, str) or len(value) < 10:
        return None
    try:
        return date.fromisoformat(value[:10]).year
    except ValueError:
        return None


def space_labels(session):
    names = []
    for attribute in session.get('attributes') or []:
        if not isinstance(attribute, dict):
            continue
        if str(attribute.get('attributeType') or '').casefold() != 'language':
            continue
        name = text(str(attribute.get('name') or attribute.get('value') or '')).casefold()
        if name:
            names.append(name)
    return names


def parse_space(payload, source, known):
    if not isinstance(payload, dict):
        raise ValueError('The Space: response is not a JSON object')
    message = payload.get('errorMessage')
    if message:
        raise ValueError('The Space: ' + text(str(message)))
    films = payload.get('result')
    if not isinstance(films, list):
        raise ValueError('The Space: result field missing or invalid')
    rows = []
    for film in films:
        if not isinstance(film, dict):
            continue
        title = text(str(film.get('filmTitle') or ''))
        if not title:
            continue
        groups = film.get('showingGroups')
        if groups is None:
            continue
        if not isinstance(groups, list):
            raise ValueError(f'The Space: invalid showingGroups for {title}')
        link = http_url(film.get('filmUrl'), '')
        year = space_year(film)
        for group in groups:
            if not isinstance(group, dict):
                continue
            sessions = group.get('sessions')
            if sessions is None:
                continue
            if not isinstance(sessions, list):
                raise ValueError(f'The Space: invalid sessions for {title}')
            for session in sessions:
                if not isinstance(session, dict):
                    continue
                day, clock = space_start(session)
                if not day:
                    continue
                names = space_labels(session)
                if 'lingua originale' in names:
                    label = 'LINGUA ORIGINALE'
                elif 'italiano' in names:
                    label = 'ITALIANO'
                else:
                    label = ' '.join(names)
                booking = session.get('bookingUrl')
                booking = urljoin(SPACE_BASE, booking) if isinstance(booking, str) and booking else ''
                rows.append(screening(source, title, day, clock, label, booking, known,
                                      year=year, source_url=link))
    return rows


def load_space(source, offset, known):
    day = (rome_today() + timedelta(days=offset)).isoformat()
    return parse_space(SPACE_CLIENT.films(day), source, known)


MANUAL_MESSAGES = {
    'massimo': 'Il sito elenca titoli, date e orari ma non la lingua per proiezione. Verificare la versione sul sito o in biglietteria.',
    'santandrea': 'Il sito Cityplex elenca titoli, date e orari ma non la lingua per proiezione. Verificare la versione sul sito o in biglietteria.',
}
MANUAL_CODES = {
    'massimo': 'source.manual.generic',
    'santandrea': 'source.manual.cityplex',
}
NOTE_CODES = ['notes.dev', 'notes.drive', 'notes.sevenDays']
LOADERS = {'arca': load_multicinema, 'universo': load_multicinema, 'uci': load_uci,
           'space': load_space}


def source_statuses(now=None):
    checked = rome_now(now).isoformat()
    return [{**source, 'status': 'manual',
             'message': MANUAL_MESSAGES.get(source['id'], 'Verifica manuale sul sito ufficiale.'),
             'checkedAt': checked,
             'messageCode': MANUAL_CODES.get(source['id'], 'source.manual.default'),
             'messageParams': {}}
            for source in SOURCES]


def gather(refresh=False):
    global CACHE, CACHE_AT
    with LOCK:
        if CACHE is not None and not refresh and time.monotonic()-CACHE_AT<CACHE_TTL:
            return CACHE
        known=metadata()
        rows=[]
        statuses={status['id']:status for status in source_statuses()}
        with ThreadPoolExecutor(max_workers=12) as pool:
            jobs={}
            for source in SOURCES:
                loader=LOADERS.get(source['id'])
                if loader is None:
                    continue
                for offset in range(DAYS):
                    jobs[pool.submit(loader,source,offset,known)]=source
            failures={}
            successes={}
            for future in as_completed(jobs):
                source=jobs[future]
                try:
                    found=future.result()
                    rows.extend(found)
                    successes[source['id']]=successes.get(source['id'],0)+1
                except Exception as exc:
                    failures.setdefault(source['id'],[]).append(str(exc))
            for sid in LOADERS:
                status=statuses.get(sid)
                if status is None:
                    continue
                days=successes.get(sid,0)
                status['status']='ok' if days==DAYS else 'error'
                status['message']=f"{days}/{DAYS} giorni letti"
                status['messageCode']='source.ok' if days==DAYS else 'source.error'
                status['messageParams']={'days':days,'total':DAYS}
                if sid in failures:
                    reason=failures[sid][0][:140]
                    status['message']+='; '+reason
                    status['messageParams']['reason']=reason
        unique={r['id']:r for r in rows}
        CACHE={'updatedAt':rome_now().isoformat(),
               'screenings':sorted(unique.values(),key=lambda r:(r['date'],r['time'],r['cinema'])),
               'sources':list(statuses.values()),
               'notes':['VERSIONE DI SVILUPPO: Massimo e Sant’Andrea richiedono verifica manuale.',
                        'Tempi di guida stimati dal centro di Pescara; non sono misure del traffico attuale.',
                        'Sette giorni di programmazione; la nazionalità italiana non dimostra la lingua originale.'],
               'noteCodes':list(NOTE_CODES)}
        try:
            tmdb.enrich(CACHE, key_path=TMDB_KEY_PATH, today=rome_today())
        except Exception:
            pass
        CACHE_AT=time.monotonic()
        return CACHE


def host_allowed(host, port):
    if not isinstance(host, str):
        return False
    return host.strip().casefold() in {f'127.0.0.1:{port}', f'localhost:{port}'}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT/'web'),**kwargs)

    def _host_ok(self):
        return host_allowed(self.headers.get('Host'), self.server.server_port)

    def _forbidden(self):
        body=json.dumps({'error':'Host non consentito'},ensure_ascii=False).encode()
        self.send_response(403)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        if self.command!='HEAD':
            self.wfile.write(body)

    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()

    def do_HEAD(self):
        if not self._host_ok():
            return self._forbidden()
        return super().do_HEAD()

    def do_GET(self):
        if not self._host_ok():
            return self._forbidden()
        path=urlparse(self.path)
        if path.path=='/health':
            return self.json_response({'status':'ok','version':'0.1-draft'})
        if path.path=='/api/screenings':
            try:
                return self.json_response(gather(parse_qs(path.query).get('refresh')==['1']))
            except Exception as exc:
                return self.json_response({'error':str(exc)},500)
        return super().do_GET()

    def json_response(self,payload,status=200):
        body=json.dumps(payload,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(body)


def main():
    parser=argparse.ArgumentParser(description='Cinema VO Pescara')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    url=f'http://127.0.0.1:{args.port}'
    print('Cinema VO: '+url,flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__=='__main__':
    main()
