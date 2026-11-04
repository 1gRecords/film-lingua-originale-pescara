"""Draft live cinema finder. Standard library only; not yet tested end to end.
Run: python cinema.py --no-browser
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import html
import json
from pathlib import Path
import re
import threading
import time
import urllib.request
from urllib.parse import urljoin, urlparse, parse_qs
import webbrowser

ROOT = Path(__file__).resolve().parent
UCI_API = 'https://myuci---uci-backend-production-nfluwp7wga-oc.a.run.app/api'
SOURCES = [
 {'id':'arca','name':"Multiplex L’Arca",'city':'Spoltore','driveMinutes':15,'url':'https://multicinema.it/Programmazione?cinema=arca'},
 {'id':'universo','name':'Multiplex Universo','city':'Silvi','driveMinutes':30,'url':'https://multicinema.it/Programmazione?cinema=universo'},
 {'id':'uci','name':'UCI Luxe Megalò','city':'Chieti','driveMinutes':30,'url':'https://www.ucicinemas.it/cinema/uci-cinemas-megalo/'},
 {'id':'massimo','name':'Cineteatro Massimo','city':'Pescara','driveMinutes':5,'url':'https://pescaracityplex.it/'},
 {'id':'santandrea','name':"Cineteatro Sant’Andrea",'city':'Pescara','driveMinutes':5,'url':'https://pescaracityplex.it/'},
 {'id':'space','name':'The Space Porto Allegro','city':'Montesilvano','driveMinutes':25,'url':'https://www.thespacecinema.it/al-cinema/montesilvano'}]
CACHE = None
CACHE_AT = 0
LOCK = threading.Lock()


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'CinemaVO/0.1 (personal local cinema finder)'})
    with urllib.request.urlopen(req, timeout=12) as response:
        data = response.read(3_000_001)
        if len(data) > 3_000_000:
            raise ValueError('Source response too large')
        return data.decode('utf-8', errors='replace')


def text(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', value))).strip()


def normalize(value):
    return re.sub(r'[^a-z0-9]', '', value.casefold())


def metadata():
    path = ROOT / 'language-overrides.json'
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8-sig'))
    return {}


def classify(label, title='', known=None):
    """A nationality is never accepted as proof of original language."""
    label = text(label).casefold()
    if re.search(r'\bdoppiat[oaie]\b|\bdubbed\b', label):
        return 'dubbed', 'Italiano doppiato', text(label)
    if re.search(r'versione originale|lingua originale|original version|\b(?:v\.?o\.?s?\.?|o\.?v\.?|vos|vost|sott\.?\s*ita)\b', label):
        return 'original', 'Versione originale', text(label)
    known = known or {}
    entry = known.get(normalize(title), known.get(title, {}))
    if entry and entry.get('language', '').casefold() in ('italiano','italian','it'):
        return 'italian', 'Italiano originale', entry.get('evidence', 'Lingua originale italiana verificata')
    return 'unknown', 'Lingua da verificare', 'Nessuna indicazione esplicita di versione originale'


def screening(source, title, day, clock, label='', booking='', known=None):
    category, language, evidence = classify(label, title, known)
    key = '|'.join((source['id'], title, day, clock, category))
    return {'id':hashlib.sha1(key.encode()).hexdigest()[:16], 'title':title,
            'cinemaId':source['id'], 'cinema':source['name'], 'city':source['city'],
            'date':day, 'time':clock, 'language':language, 'classification':category,
            'evidence':evidence, 'sourceUrl':source['url'], 'bookingUrl':booking or source['url'],
            'driveMinutes':source['driveMinutes']}


def parse_multicinema(raw, source, day, known):
    rows=[]
    # Restrict to daily listing nodes; sidebar events must not leak into screenings.
    chunks = re.split(r'<div\s+class="item_small"\s+ng-repeat="pr in getProgrammazioneGiornoSel\(\)"', raw)[1:]
    for chunk in chunks:
        chunk = chunk.split('<!-- .grid_9',1)[0]
        heading = re.search(r'<h3>\s*<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>\s*</h3>', chunk, re.S)
        if not heading:
            continue
        title = text(heading.group(2))
        times = re.search(r'<div class="tagcloud_orari">(.*?)</div>',chunk,re.S)
        notes = ' '.join(re.findall(r'<span class="prog_nota\d">(.*?)</span>',chunk,re.S))
        if not times:
            continue
        for h,m in re.findall(r'\b([0-2]?\d)[.:]([0-5]\d)\b',text(times.group(1))):
            if int(h)>23:
                continue
            rows.append(screening(source,title,day,f'{int(h):02}:{m}',notes,
                                  urljoin(source['url'],html.unescape(heading.group(1))),known))
    return rows


def load_multicinema(source, offset, known):
    day = (date.today()+timedelta(days=offset)).isoformat()
    raw = fetch(source['url']+'&giornoSettimana='+str(offset))
    return parse_multicinema(raw,source,day,known)


def parse_uci(payload, source, known):
    rows=[]
    for movie in payload.get('data',[]):
        for screens in movie.get('screens',[]):
            for versions in screens.values():
                for version in versions:
                    lang = (version.get('language') or {}).get('slug','')
                    subtitle = (version.get('subtitles') or {})
                    label = lang+' '+(subtitle.get('name','') if isinstance(subtitle,dict) else str(subtitle))
                    for show in version.get('performances',[]):
                        clock = show.get('actual_start_at') or show.get('starts_at','')[11:16]
                        if not re.fullmatch(r'\d{2}:\d{2}',clock):
                            continue
                        row = screening(source,movie['title'],show['day'],clock,label,
                                        urljoin('https://www.ucicinemas.it',show.get('cart_link','')),known)
                        if lang.upper() not in ('ITA','IT','ITALIANO',''):
                            row.update(classification='original',language=lang+' · originale',
                                       evidence='Lingua della proiezione indicata da UCI: '+label)
                        rows.append(row)
    return rows


def load_uci(source, offset, known):
    day=(date.today()+timedelta(days=offset)).isoformat()
    return parse_uci(json.loads(fetch(UCI_API+'/theatres/uci-cinemas-megalo/programming/'+day)),source,known)


def gather(refresh=False):
    global CACHE, CACHE_AT
    with LOCK:
        if CACHE is not None and not refresh and time.monotonic()-CACHE_AT<600:
            return CACHE
        known=metadata()
        rows=[]
        statuses={s['id']:{**s,'status':'manual','checkedAt':datetime.now().astimezone().isoformat(),
                           'message':'Consultare il sito: integrazione automatica non ancora completata'} for s in SOURCES}
        with ThreadPoolExecutor(max_workers=12) as pool:
            jobs={}
            for source in SOURCES[:3]:
                for offset in range(7):
                    fn=load_uci if source['id']=='uci' else load_multicinema
                    jobs[pool.submit(fn,source,offset,known)]=source
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
            for source in SOURCES[:3]:
                sid=source['id']
                status=statuses[sid]
                status['status']='ok' if successes.get(sid)==7 else 'error'
                status['message']=f"{successes.get(sid,0)}/7 giorni letti"
                if sid in failures:
                    status['message']+='; '+failures[sid][0][:140]
        unique={r['id']:r for r in rows}
        CACHE={'updatedAt':datetime.now().astimezone().isoformat(),
               'screenings':sorted(unique.values(),key=lambda r:(r['date'],r['time'],r['cinema'])),
               'sources':list(statuses.values()),
               'notes':['VERSIONE DI SVILUPPO: Massimo, Sant’Andrea e The Space richiedono verifica manuale.',
                        'Tempi di guida stimati dal centro di Pescara; non sono misure del traffico attuale.',
                        'Sette giorni di programmazione; la nazionalità italiana non dimostra la lingua originale.']}
        CACHE_AT=time.monotonic()
        return CACHE


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT/'web'),**kwargs)

    def do_GET(self):
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
