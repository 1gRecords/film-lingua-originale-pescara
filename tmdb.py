"""TMDB ratings and plots for the cinema list. Standard library only.

The API token is read from tmdb-key.txt and sent only to api.themoviedb.org.
Results are cached on disk so a refresh does not repeat TMDB calls.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
import json
from pathlib import Path
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
KEY_PATH = ROOT / 'tmdb-key.txt'
CACHE_PATH = ROOT / 'tmdb-cache.json'
OVERRIDES_PATH = ROOT / 'tmdb-overrides.json'
API = 'https://api.themoviedb.org/3'
SITE = 'https://www.themoviedb.org'
CACHE_TTL = 30 * 24 * 60 * 60
# Bump when matching rules change: cached matches from older rules must not survive.
CACHE_VERSION = 2
MAX_WORKERS = 4
MIN_VOTE_COUNT = 50
USER_AGENT = 'CinemaVO/0.1 (personal local cinema finder)'

_PAREN_SUFFIX = re.compile(
    r'\s*[\(\[]\s*(?:lingua\s+originale|versione\s+originale|original\s+version|'
    r'v\.?\s?o\.?s?)\s*[\)\]]\s*$', re.I)
_TEXT_SUFFIX = re.compile(
    r'(?:\s*[-–—:|]\s*|\s+)(?:lingua\s+originale|versione\s+originale|'
    r'original\s+version|v\.?\s?o\.?s?|c\.\s?a\.)\s*$', re.I)


class TmdbError(Exception):
    pass


class RateLimited(TmdbError):
    def __init__(self, retry_after=1.0):
        super().__init__('TMDB rate limit')
        self.retry_after = retry_after


def clean_title(value):
    """Drop the cinema's original-language suffixes, not the film's own text."""
    title = re.sub(r'\s+', ' ', str(value or '')).strip()
    while title:
        cleaned = _PAREN_SUFFIX.sub('', title)
        cleaned = _TEXT_SUFFIX.sub('', cleaned).strip(' -–—:|…').strip()
        if cleaned == title:
            break
        title = cleaned
    return title


def normalize_title(value):
    decomposed = unicodedata.normalize('NFKD', str(value or ''))
    plain = ''.join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', plain.casefold())).strip()


def parse_year(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and 1000 <= value <= 3000:
        return value
    match = re.match(r'\s*(\d{4})', str(value or ''))
    if match:
        return int(match.group(1))
    return None


def film_key(cleaned, year=None):
    base = normalize_title(cleaned)
    return f'{base}|{year}' if year is not None else base


def cache_key(cleaned, year=None, override=None):
    key = film_key(cleaned, year)
    return f'{key}|ov:{override}' if override is not None else key


def parse_release_date(item):
    match = re.match(r'\s*(\d{4})-(\d{2})-(\d{2})',
                     str((item or {}).get('release_date') or ''))
    if not match:
        return None
    try:
        return date(*map(int, match.groups()))
    except ValueError:
        return None


def release_year(item):
    released = parse_release_date(item)
    return released.year if released else None


def released_too_long_ago(item, today, years=2):
    released = parse_release_date(item)
    if released is None or today is None:
        return False
    try:
        cutoff = today.replace(year=today.year - years)
    except ValueError:
        cutoff = today.replace(year=today.year - years, day=28)
    return released < cutoff


def select_match(cleaned, results, year=None, today=None):
    """Return (candidate, reason) and never guess between two exact titles."""
    target = normalize_title(cleaned)
    usable = [item for item in (results or []) if isinstance(item, dict)]
    if not target:
        return None, 'empty title'
    if not usable:
        return None, 'no results'
    original_count = len(usable)
    if year is None and today is not None:
        recent = [item for item in usable if not released_too_long_ago(item, today)]
        if not recent:
            return None, 'released more than 2 years before today'
        usable = recent
    exact = [item for item in usable
             if target in (normalize_title(item.get('title')),
                           normalize_title(item.get('original_title')))]
    if year is not None:
        with_year = [item for item in exact
                     if release_year(item) is not None
                     and abs(release_year(item) - year) <= 1]
        if exact and not with_year:
            return None, 'year mismatch'
        exact = with_year
    if len(exact) == 1:
        return exact[0], 'exact'
    if len(exact) > 1:
        return None, 'ambiguous: multiple exact titles'
    if original_count != 1:
        return None, 'no exact title match'
    only = usable[0]
    only_year = release_year(only)
    if year is not None and only_year is None:
        return None, 'year unavailable on TMDB result'
    if year is not None and abs(only_year - year) > 1:
        return None, 'year mismatch'
    votes = only.get('vote_count')
    if isinstance(votes, bool) or not isinstance(votes, int) or votes < MIN_VOTE_COUNT:
        return None, f'single result below {MIN_VOTE_COUNT} votes'
    return only, 'single result'


def read_token(path=KEY_PATH):
    try:
        value = Path(path).read_text(encoding='utf-8-sig').strip()
    except OSError:
        return ''
    if value.casefold().startswith('bearer '):
        value = value[7:].strip()
    if len(value) < 20 or any(char.isspace() for char in value):
        return ''
    return value


def normalize_overrides(raw):
    result = {}
    if not isinstance(raw, dict):
        return result
    for key, value in raw.items():
        base = normalize_title(clean_title(key))
        if not base:
            continue
        if value is None:
            result[base] = None
        elif isinstance(value, int) and not isinstance(value, bool) and value > 0:
            result[base] = value
        elif isinstance(value, str) and value.strip().isdigit() and int(value) > 0:
            result[base] = int(value)
    return result


def load_overrides(path=OVERRIDES_PATH):
    try:
        raw = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return {}
    return normalize_overrides(raw)


def load_cache(path=CACHE_PATH):
    try:
        raw = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict) or raw.get('version') != CACHE_VERSION:
        return {}
    entries = raw.get('entries')
    return entries if isinstance(entries, dict) else {}


def cache_fresh(entry, now):
    if not isinstance(entry, dict):
        return False
    fetched = entry.get('at')
    if isinstance(fetched, bool) or not isinstance(fetched, (int, float)):
        return False
    return 0 <= now - fetched <= CACHE_TTL


def save_cache(path, entries, now):
    if path is None:
        return
    fresh = {key: value for key, value in entries.items() if cache_fresh(value, now)}
    target = Path(path)
    temporary = target.with_suffix(target.suffix + '.tmp')
    try:
        temporary.write_text(json.dumps({'version': CACHE_VERSION, 'entries': fresh},
                                        ensure_ascii=False, separators=(',', ':')),
                             encoding='utf-8')
        temporary.replace(target)
    except OSError:
        pass


def http_transport(url, headers):
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read(2_000_001)
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            try:
                retry_after = float(exc.headers.get('Retry-After') or 1)
            except (TypeError, ValueError):
                retry_after = 1.0
            raise RateLimited(retry_after) from exc
        raise TmdbError(f'HTTP {exc.code}') from exc
    except Exception as exc:
        raise TmdbError(str(exc)) from exc
    if len(payload) > 2_000_000:
        raise TmdbError('response too large')
    try:
        return json.loads(payload)
    except ValueError as exc:
        raise TmdbError('invalid JSON') from exc


class TmdbClient:
    def __init__(self, token, transport=None, sleep=time.sleep):
        self.token = token
        self.transport = transport or http_transport
        self.sleep = sleep

    def _get(self, path, params):
        url = API + path + '?' + urllib.parse.urlencode(params)
        headers = {'Authorization': 'Bearer ' + self.token,
                   'Accept': 'application/json',
                   'User-Agent': USER_AGENT}
        try:
            return self.transport(url, headers)
        except RateLimited as exc:
            delay = min(max(float(exc.retry_after or 0), 1.0), 5.0)
            self.sleep(delay)
            return self.transport(url, headers)

    def search(self, cleaned, year=None):
        attempts = [('it-IT', year), ('it-IT', None)]
        if year is not None:
            attempts += [('en-US', year), ('en-US', None)]
        else:
            attempts.append(('en-US', None))
        for language, attempt_year in attempts:
            params = {'query': cleaned, 'language': language}
            if attempt_year is not None:
                params['year'] = attempt_year
            payload = self._get('/search/movie', params)
            results = payload.get('results') if isinstance(payload, dict) else None
            if isinstance(results, list):
                usable = [item for item in results if isinstance(item, dict)]
                if usable:
                    return usable
        return []

    def details(self, film_id):
        film_id = int(film_id)
        italian = self._get(f'/movie/{film_id}', {'language': 'it-IT'})
        if not isinstance(italian, dict):
            raise TmdbError('invalid detail response')
        english = {}
        try:
            candidate = self._get(f'/movie/{film_id}', {'language': 'en-US'})
            if isinstance(candidate, dict):
                english = candidate
        except TmdbError:
            pass

        def value(field):
            for document in (italian, english):
                found = document.get(field)
                if isinstance(found, str) and found.strip():
                    return found.strip()
            return ''

        rating = italian.get('vote_average', english.get('vote_average'))
        if isinstance(rating, bool) or not isinstance(rating, (int, float)):
            rating = None
        votes = italian.get('vote_count', english.get('vote_count'))
        if isinstance(votes, bool) or not isinstance(votes, (int, float)):
            votes = 0
        votes = int(votes)
        if votes <= 0:
            rating = None
        overview_it = italian.get('overview')
        overview_en = english.get('overview')
        return {
            'id': film_id,
            'title': value('title') or value('original_title'),
            'originalTitle': value('original_title'),
            'year': parse_year(value('release_date')),
            'rating': round(float(rating), 1) if rating is not None else None,
            'votes': votes,
            'overviewIt': overview_it.strip() if isinstance(overview_it, str) else '',
            'overviewEn': overview_en.strip() if isinstance(overview_en, str) else '',
            'url': f'{SITE}/movie/{film_id}',
        }

    def resolve(self, cleaned, year=None, override=None, today=None):
        if override is not None:
            return self.details(override), 'override'
        results = self.search(cleaned, year)
        match, reason = select_match(cleaned, results, year, today)
        if match is None:
            return None, reason
        return self.details(match['id']), 'found'


def enrich(payload, key_path=KEY_PATH, cache_path=CACHE_PATH,
           overrides_path=OVERRIDES_PATH, transport=None, token=None,
           cache=None, overrides=None, now=None, today=None):
    """Attach tmdb.films and screening.tmdbKey; never raise to the caller."""
    if not isinstance(payload, dict):
        return payload
    try:
        token = token or read_token(key_path)
        if not token:
            return payload
        rows = payload.get('screenings')
        if not isinstance(rows, list) or not rows:
            return payload
        current = time.time() if now is None else float(now)
        today = date.today() if today is None else today
        overrides = (load_overrides(overrides_path) if overrides is None
                     else normalize_overrides(overrides))
        entries = cache if isinstance(cache, dict) else (
            load_cache(cache_path) if cache_path is not None else {})
        client = TmdbClient(token, transport=transport)

        tasks = {}
        row_keys = []
        blocked = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('title'), str):
                continue
            cleaned = clean_title(row['title'])
            year = parse_year(row.get('year'))
            base = normalize_title(cleaned)
            if not base:
                continue
            key = film_key(cleaned, year)
            if base in overrides:
                override = overrides[base]
                if override is None:
                    blocked.add(key)
                    row_keys.append((row, None, key))
                    continue
            else:
                override = None
            lookup = cache_key(cleaned, year, override)
            tasks.setdefault(lookup, (cleaned, year, override))
            row_keys.append((row, lookup, key))

        films = {}
        misses = {}
        pending = []
        for lookup, (cleaned, year, override) in tasks.items():
            entry = entries.get(lookup)
            key = film_key(cleaned, year)
            if cache_fresh(entry, current):
                if isinstance(entry.get('film'), dict):
                    films[key] = entry['film']
                else:
                    misses[key] = str(entry.get('miss') or 'cached miss')
            else:
                pending.append((lookup, cleaned, year, override))

        for key in blocked:
            misses[key] = 'blocked by override'

        if pending:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
                jobs = {pool.submit(client.resolve, cleaned, year, override, today):
                        (lookup, cleaned, year)
                        for lookup, cleaned, year, override in pending}
                for future in as_completed(jobs):
                    lookup, cleaned, year = jobs[future]
                    key = film_key(cleaned, year)
                    try:
                        film, reason = future.result()
                    except Exception as exc:
                        film, reason = None, 'TMDB error: ' + str(exc)[:100]
                    if film:
                        films[key] = film
                        entries[lookup] = {'at': current, 'film': film}
                    else:
                        misses[key] = reason
                        if not str(reason).startswith('TMDB error'):
                            entries[lookup] = {'at': current, 'miss': reason}

        for row, lookup, key in row_keys:
            row.pop('tmdbKey', None)
            if lookup is not None and key in films:
                row['tmdbKey'] = key

        payload['tmdb'] = {'enabled': True, 'site': SITE,
                           'films': films, 'misses': misses}
        if pending:
            save_cache(cache_path, entries, current)
        return payload
    except Exception:
        return payload
