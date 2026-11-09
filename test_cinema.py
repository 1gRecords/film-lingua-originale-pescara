"""Offline tests for the cinema backend.

Every fixture is inline. Nothing in this module opens a socket, so the suite
also proves that the parsers do not depend on the live sites.
"""
import copy
import json
import re
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

import cinema
import tmdb


UI_JS_PATH = Path(__file__).resolve().parent / 'web' / 'app.js'


def ui_dictionaries(source):
    """Return {'it': {key: raw_value}, 'en': {...}} parsed from web/app.js text.

    Each dictionary is a `  it: {` or `  en: {` block that closes on a line
    holding only `  }`, with one `'key': 'value',` entry per line.
    """
    dictionaries = {}
    for lang, body in re.findall(r'^  (it|en): \{\n(.*?)^  \}', source, re.M | re.S):
        dictionaries[lang] = dict(
            re.findall(r"^[ \t]*'([^']+)'[ \t]*:[ \t]*(.*?)[ \t]*,?[ \t]*$", body, re.M)
        )
    return dictionaries


class UiDictionaryParityTest(unittest.TestCase):
    def test_it_and_en_have_same_keys(self):
        dictionaries = ui_dictionaries(UI_JS_PATH.read_text(encoding='utf-8'))
        it_entries = dictionaries.get('it', {})
        en_entries = dictionaries.get('en', {})
        self.assertTrue(it_entries, 'no it entries found in web/app.js')
        self.assertTrue(en_entries, 'no en entries found in web/app.js')
        missing_in_en = sorted(set(it_entries) - set(en_entries))
        missing_in_it = sorted(set(en_entries) - set(it_entries))
        self.assertFalse(
            missing_in_en or missing_in_it,
            f'keys missing in en: {missing_in_en}; keys missing in it: {missing_in_it}',
        )
        empty = sorted(
            f'{lang}:{key}'
            for lang, entries in dictionaries.items()
            for key, raw in entries.items()
            if raw == "''"
        )
        self.assertEqual(empty, [], 'empty translation values in web/app.js')


KNOWN = {
    'italian film': {
        'title': 'Italian Film',
        'year': 2026,
        'language': 'it',
        'evidence': 'Scheda film: lingua originale italiana.',
    },
    'english film': {
        'title': 'English Film',
        'year': 2026,
        'language': 'en',
        'evidence': 'Scheda film: lingua originale inglese.',
    },
    'dio ride': {
        'title': 'Dio ride',
        'year': 2026,
        'language': 'it',
        'evidence': 'Scheda film: lingua originale italiana.',
    },
}

AMBIGUOUS = {
    'old': {'title': 'Remake', 'year': 2001, 'language': 'en'},
    'new': {'title': 'Remake', 'year': 2019, 'language': 'it'},
}

ARCA_SOURCE = {
    'id': 'arca',
    'name': 'Multiplex Arca',
    'city': 'Spoltore',
    'driveMinutes': 15,
    'url': 'https://multicinema.it/Programmazione?cinema=arca',
}

UCI_SOURCE = {
    'id': 'uci',
    'name': 'UCI Luxe Megalo',
    'city': 'Chieti',
    'driveMinutes': 30,
    'url': 'https://www.ucicinemas.it/cinema/uci-cinemas-megalo/',
}

SPACE_SOURCE = {
    'id': 'space',
    'name': 'The Space Porto Allegro',
    'city': 'Montesilvano',
    'driveMinutes': 25,
    'url': 'https://www.thespacecinema.it/cinema/montesilvano/al-cinema',
}

TEST_SOURCE = {
    'id': 'test',
    'name': 'Cinema Test',
    'city': 'Pescara',
    'driveMinutes': 5,
    'url': 'https://example.com/program',
}

ARCA_HTML = '''
<div class="item_small" ng-repeat="pr in getProgrammazioneGiornoSel()" ng-show="getProgrammazioneGiornoSel().length > 0">
  <div class="one_post"><div class="item-details-prog">
    <h3><a href="/Film/Scheda/6823?titolo=Fast" rel="bookmark">Fast and Furious - 25&#176; Anniversario</a></h3>
    <div class="tagcloud_orari">
      <a ng-repeat="o in pr.orario.split(' ')">17.40</a>
      <a ng-repeat="o in pr.orario.split(' ')">21.20</a>
    </div>
    <div class="post_meta_note"><span class="prog_nota1">VERSIONE ORIGINALE SOTTOTITOLATA IN ITALIANO</span></div>
  </div></div>
</div>
<div class="item_small" ng-repeat="pr in getProgrammazioneGiornoSel()" ng-show="getProgrammazioneGiornoSel().length > 0">
  <div class="one_post"><div class="item-details-prog">
    <h3><a href="/Film/Scheda/6809?titolo=Dio-ride">Dio ride</a></h3>
    <div class="tagcloud_orari"><a ng-repeat="o in pr.orario.split(' ')">18.15</a></div>
    <div class="post_meta_note"><span class="prog_nota1">VM18</span></div>
  </div></div>
</div>
<div class="item_small" ng-repeat="ev in eventi">
  <div class="item-details-prog">
    <h3><a href="/Eventi/1">Anteprima: Dune</a></h3>
    <div class="tagcloud_orari"><a>20.00</a></div>
    <div class="post_meta_note"><span class="prog_nota1">VERSIONE ORIGINALE</span></div>
  </div>
</div>
<div class="item_small" ng-repeat="pr in footer.prossimamente">
  <div class="item-details-prog">
    <h3><a href="/Film/Scheda/9">Wild Horse Nine</a></h3>
    <div class="tagcloud_orari"><a>21.00</a></div>
    <div class="post_meta_note"><span class="prog_nota1">VERSIONE ORIGINALE</span></div>
  </div>
</div>
<div class="item_small" ng-repeat="pr in getProgrammazioneGiornoSel()" ng-show="getProgrammazioneGiornoSel().length > 0">
  <div class="one_post"><div class="item-details-prog">
    <h3><a href="/Film/Scheda/10">Senza orari</a></h3>
    <div class="post_meta_note"><span class="prog_nota1">VERSIONE ORIGINALE</span></div>
  </div></div>
</div>
'''

UCI_JSON = '''
{
  "data": [
    {"title": "Dio ride", "screens": [{"2D": [{
      "language": {"name": "ITA", "slug": "ITA"},
      "subtitles": null,
      "performances": [
        {"day": "2026-11-04", "actual_start_at": "18:50", "starts_at": "2026-11-04 18:50:00",
         "cart_link": "/movies/dio-ride/acquista/5664/2968/45550"}
      ]
    }]}]},
    {"title": "Foreign Film", "screens": [{"2D": [{
      "language": {"name": "EN", "slug": "EN"},
      "subtitles": {"name": "ITALIANO"},
      "performances": [
        {"day": "2026-11-04", "actual_start_at": "20:00", "cart_link": "/movies/foreign/acquista/1"}
      ]
    }]}]},
    {"title": "Korean Film", "screens": [{"2D": [{
      "language": {"name": "KOR", "slug": "KOR"},
      "performances": [
        {"day": "2026-11-04", "starts_at": "2026-11-04 21:30:00", "cart_link": ""}
      ]
    }]}]},
    {"title": "No Language", "screens": [{"2D": [{
      "subtitles": null,
      "performances": [{"day": "2026-11-04", "actual_start_at": "22:00"}]
    }]}]},
    {"title": "Bad Day", "screens": [{"2D": [{
      "language": {"slug": "ITA"},
      "performances": [{"actual_start_at": "22:10"}]
    }]}]},
    {"title": "Bad Time", "screens": [{"2D": [{
      "language": {"slug": "ITA"},
      "performances": [{"day": "2026-11-04", "actual_start_at": "99:99", "starts_at": "not-a-time"}]
    }]}]},
    {"screens": [{"2D": [{
      "language": {"slug": "ITA"},
      "performances": [{"day": "2026-11-04", "actual_start_at": "23:00"}]
    }]}]},
    {"title": "Empty", "screens": []},
    {"title": "No Screens"},
    "not a movie"
  ]
}
'''


SPACE_JSON = '''
{
  "responseCode": 200,
  "errorMessage": null,
  "result": [
    {
      "filmTitle": "FAST & FURIOUS - 25MO ANNIVERSARIO",
      "filmUrl": "https://www.thespacecinema.it/film/fast-and-furious",
      "releaseDate": "2026-10-29T00:00:00",
      "showingGroups": [{"date": "2026-11-05T00:00:00", "sessions": [
        {"sessionId": "1", "startTime": "2026-11-05T16:10:00",
         "showTimeWithTimeZone": "2026-11-05T16:10:00+01:00",
         "bookingUrl": "/prenotare-il-biglietto/summary/1026/HO1/1",
         "attributes": [{"name": "ITALIANO", "attributeType": "Language"},
                        {"name": "2D", "attributeType": "Session"}]},
        {"sessionId": "2", "startTime": "2026-11-05T18:20:00",
         "bookingUrl": "/prenotare-il-biglietto/summary/1026/HO1/2",
         "attributes": [{"name": "ITALIANO", "attributeType": "Language"}]},
        {"sessionId": "3", "startTime": "2026-11-05T21:30:00",
         "bookingUrl": "/prenotare-il-biglietto/summary/1026/HO1/3",
         "attributes": [{"name": "ITALIANO", "attributeType": "Language"}]},
        {"sessionId": "4", "startTime": "2026-11-05T18:50:00",
         "bookingUrl": "/prenotare-il-biglietto/summary/1026/HO1/4",
         "attributes": [{"name": "LINGUA ORIGINALE", "attributeType": "Language"},
                        {"name": "2D", "attributeType": "Session"}]}
      ]}]
    },
    {
      "filmTitle": "DIO RIDE",
      "filmUrl": "https://www.thespacecinema.it/film/dio-ride",
      "releaseDate": "2026-10-29T00:00:00",
      "showingGroups": [{"date": "2026-11-05T00:00:00", "sessions": [
        {"sessionId": "5", "startTime": "2026-11-05T16:00:00",
         "attributes": [{"name": "ITALIANO", "attributeType": "Language"}]},
        {"sessionId": "6", "startTime": "2026-11-05T18:45:00",
         "attributes": [{"name": "LINGUA ORIGINALE", "attributeType": "Language"}]}
      ]}]
    },
    {
      "filmTitle": "English Film",
      "filmUrl": "https://www.thespacecinema.it/film/english-film",
      "releaseDate": "2026-01-01T00:00:00",
      "showingGroups": [{"date": "2026-11-05T00:00:00", "sessions": [
        {"sessionId": "7", "startTime": "2026-11-05T20:00:00",
         "attributes": [{"name": "ITALIANO", "attributeType": "Language"}]},
        {"sessionId": "8", "startTime": "not-a-time",
         "attributes": [{"name": "ITALIANO", "attributeType": "Language"}]}
      ]}]
    },
    {
      "filmTitle": "No Attributes",
      "filmUrl": "https://www.thespacecinema.it/film/no-attributes",
      "showingGroups": [{"date": "2026-11-05T00:00:00", "sessions": [
        {"sessionId": "9", "startTime": "2026-11-05T21:00:00"}
      ]}]
    },
    {
      "filmTitle": "Unknown Language",
      "showingGroups": [{"date": "2026-11-05T00:00:00", "sessions": [
        {"sessionId": "10", "startTime": "2026-11-05T22:00:00",
         "attributes": [{"name": "SPAGNOLO", "attributeType": "Language"}]}
      ]}]
    },
    {
      "filmTitle": "Italian Film",
      "releaseDate": "2010-01-01T00:00:00",
      "showingGroups": [{"date": "2026-11-05T00:00:00", "sessions": [
        {"sessionId": "11", "startTime": "2026-11-05T22:15:00",
         "attributes": [{"name": "ITALIANO", "attributeType": "Language"}]}
      ]}]
    },
    {
      "filmTitle": "Midnight",
      "showingGroups": [{"date": "2026-11-05T00:00:00", "sessions": [
        {"sessionId": "12", "startTime": "2026-11-06T00:15:00"}
      ]}]
    },
    {"filmTitle": ""},
    "not a film"
  ]
}
'''


class RomeClockTests(unittest.TestCase):
    def test_winter_uses_plus_one(self):
        moment = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)
        self.assertEqual(cinema.rome_now(moment).isoformat(), '2026-11-04T13:00:00+01:00')

    def test_naive_input_is_treated_as_utc(self):
        moment = datetime(2026, 11, 4, 12, 0)
        self.assertEqual(cinema.rome_now(moment).isoformat(), '2026-11-04T13:00:00+01:00')

    def test_summer_uses_plus_two(self):
        moment = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
        self.assertEqual(cinema.rome_now(moment).isoformat(), '2026-07-15T14:00:00+02:00')

    def test_dst_starts_at_0100_utc_on_last_sunday_of_march(self):
        before = datetime(2026, 3, 29, 0, 59, tzinfo=timezone.utc)
        after = datetime(2026, 3, 29, 1, 0, tzinfo=timezone.utc)
        self.assertEqual(cinema.rome_now(before).isoformat(), '2026-03-29T01:59:00+01:00')
        self.assertEqual(cinema.rome_now(after).isoformat(), '2026-03-29T03:00:00+02:00')

    def test_dst_ends_at_0100_utc_on_last_sunday_of_october(self):
        before = datetime(2026, 10, 25, 0, 59, tzinfo=timezone.utc)
        after = datetime(2026, 10, 25, 1, 0, tzinfo=timezone.utc)
        self.assertEqual(cinema.rome_now(before).isoformat(), '2026-10-25T02:59:00+02:00')
        self.assertEqual(cinema.rome_now(after).isoformat(), '2026-10-25T02:00:00+01:00')

    def test_year_rollover_uses_the_new_local_day(self):
        moment = datetime(2026, 12, 31, 23, 30, tzinfo=timezone.utc)
        self.assertEqual(cinema.rome_today(moment).isoformat(), '2027-01-01')


class NormalizationTests(unittest.TestCase):
    def test_case_accents_punctuation_and_spaces(self):
        self.assertEqual(cinema.normalize('  L\u2019Estranea!!  '), 'l estranea')
        self.assertEqual(cinema.normalize('D\u00eco   R\u00ecde'), 'dio ride')
        self.assertEqual(cinema.normalize("Je so' pazzo"), 'je so pazzo')
        self.assertEqual(cinema.normalize(''), '')

    def test_override_key_and_title_are_normalized_together(self):
        known = {'D\u00ecO  R\u00ecDE': {'title': 'Dio ride', 'year': 2026, 'language': 'it'}}
        self.assertIsNotNone(cinema.match_override('DIO RIDE', 2026, known))
        self.assertIsNone(cinema.match_override('DIO RIDE', 2018, known))

    def test_year_match_ambiguity_and_title_only(self):
        self.assertEqual(cinema.match_override('Remake', 2019, AMBIGUOUS)['language'], 'it')
        self.assertIsNone(cinema.match_override('Remake', 1999, AMBIGUOUS))
        self.assertIsNone(cinema.match_override('Remake', None, AMBIGUOUS))
        self.assertIsNotNone(cinema.match_override('Italian Film', None, KNOWN))
        self.assertIsNotNone(cinema.match_override('Italian Film', 2026, KNOWN))
        self.assertIsNone(cinema.match_override('Italian Film', 2018, KNOWN))


class ClassificationTests(unittest.TestCase):
    def check(self, expected, **kwargs):
        category, _language, _evidence = cinema.classify(**kwargs)
        self.assertEqual(category, expected)

    def test_truth_table(self):
        cases = [
            ('explicit dubbed label',
             dict(label='DOPPIATO', title='Italian Film', known=KNOWN, year=2026), 'dubbed'),
            ('explicit VOS label',
             dict(label='VOS', title='Sconosciuto', known=KNOWN), 'original'),
            ('explicit original version label',
             dict(label='versione originale', title='Sconosciuto', known=KNOWN), 'original'),
            ('verified Italian wins over a VO label',
             dict(label='VERSIONE ORIGINALE', title='Italian Film', known=KNOWN, year=2026), 'italian'),
            ('verified Italian with Italian audio',
             dict(label='', title='Italian Film', known=KNOWN, audio_lang='ITA', year=2026), 'italian'),
            ('verified Italian with foreign audio is dubbed',
             dict(label='', title='Italian Film', known=KNOWN, audio_lang='EN', year=2026), 'dubbed'),
            ('verified English with English audio is original',
             dict(label='', title='English Film', known=KNOWN, audio_lang='ENG', year=2026), 'original'),
            ('verified English with Italian audio is dubbed',
             dict(label='', title='English Film', known=KNOWN, audio_lang='ITA', year=2026), 'dubbed'),
            ('foreign audio without metadata is unknown',
             dict(label='', title='Sconosciuto', known=KNOWN, audio_lang='KOR'), 'unknown'),
            ('bare ITA label is not proof',
             dict(label='ITA', title='Sconosciuto', known=KNOWN, audio_lang='ITA'), 'unknown'),
            ('verified metadata without audio is not enough',
             dict(label='', title='English Film', known=KNOWN), 'unknown'),
            ('metadata mismatch beats a VO label',
             dict(label='versione originale', title='Italian Film', known=KNOWN,
                  audio_lang='EN', year=2026), 'dubbed'),
            ('dubbed label beats an Italian override',
             dict(label='dubbed', title='Italian Film', known=KNOWN,
                  audio_lang='ITA', year=2026), 'dubbed'),
            ('VO label still works without metadata',
             dict(label='versione originale', title='English Film', known=KNOWN), 'original'),
        ]
        for name, kwargs, expected in cases:
            with self.subTest(name):
                self.check(expected, **kwargs)

    def test_title_only_match_discloses_the_missing_year(self):
        category, _language, evidence = cinema.classify('', 'Italian Film', KNOWN, year=None)
        self.assertEqual(category, 'italian')
        self.assertIn('anno non disponibile', evidence)

    def test_known_year_mismatch_rejects_the_override(self):
        category, _language, _evidence = cinema.classify('', 'Italian Film', KNOWN, year=2018)
        self.assertEqual(category, 'unknown')

    def test_ambiguous_title_is_not_matched(self):
        category, _language, _evidence = cinema.classify('', 'Remake', AMBIGUOUS, year=None)
        self.assertEqual(category, 'unknown')


class ArcaParserTests(unittest.TestCase):
    def setUp(self):
        self.rows = cinema.parse_multicinema(ARCA_HTML, ARCA_SOURCE, '2026-11-04', {})
        self.titles = [row['title'] for row in self.rows]

    def test_rows_come_only_from_daily_blocks(self):
        self.assertEqual(len(self.rows), 3)
        self.assertEqual(self.titles.count('Anteprima: Dune'), 0)
        self.assertEqual(self.titles.count('Wild Horse Nine'), 0)
        self.assertEqual(self.titles.count('Senza orari'), 0)

    def test_vo_note_applies_to_every_time_in_its_block_only(self):
        fast = [row for row in self.rows if row['title'].startswith('Fast and Furious')]
        self.assertEqual([row['time'] for row in fast], ['17:40', '21:20'])
        self.assertTrue(all(row['classification'] == 'original' for row in fast))
        self.assertTrue(all('scheda giornaliera' in row['evidence'] for row in fast))
        self.assertTrue(all('versione originale' in row['evidence'].casefold() for row in fast))

    def test_note_does_not_leak_to_the_next_film(self):
        dio = next(row for row in self.rows if row['title'] == 'Dio ride')
        self.assertEqual(dio['classification'], 'unknown')

    def test_all_rows_use_the_requested_day(self):
        self.assertTrue(all(row['date'] == '2026-11-04' for row in self.rows))
        self.assertTrue(all(row['sourceUrl'] == ARCA_SOURCE['url'] for row in self.rows))

    def test_missing_heading_or_times_produces_no_rows(self):
        raw = '<div class="item_small" ng-repeat="pr in getProgrammazioneGiornoSel()"><div class="tagcloud_orari"><a>18.00</a></div></div>'
        self.assertEqual(cinema.parse_multicinema(raw, ARCA_SOURCE, '2026-11-04', KNOWN), [])


class UciParserTests(unittest.TestCase):
    def setUp(self):
        self.rows = cinema.parse_uci(json.loads(UCI_JSON), UCI_SOURCE, KNOWN)
        self.by_title = {row['title']: row for row in self.rows}

    def test_bad_rows_are_skipped_and_good_rows_survive(self):
        self.assertEqual(len(self.rows), 4)
        self.assertNotIn('Bad Day', self.by_title)
        self.assertNotIn('Bad Time', self.by_title)
        self.assertNotIn('Empty', self.by_title)
        self.assertNotIn('No Screens', self.by_title)

    def test_italian_audio_plus_verified_italian_is_italian(self):
        self.assertEqual(self.by_title['Dio ride']['classification'], 'italian')

    def test_non_italian_audio_is_unknown_without_metadata(self):
        self.assertEqual(self.by_title['Foreign Film']['classification'], 'unknown')
        self.assertEqual(self.by_title['Korean Film']['classification'], 'unknown')
        self.assertNotEqual(self.by_title['Korean Film']['classification'], 'original')

    def test_missing_language_is_unknown(self):
        self.assertEqual(self.by_title['No Language']['classification'], 'unknown')

    def test_missing_start_time_falls_back_to_starts_at(self):
        self.assertEqual(self.by_title['Korean Film']['time'], '21:30')

    def test_cart_link_is_joined_to_the_uci_host(self):
        self.assertEqual(
            self.by_title['Dio ride']['bookingUrl'],
            'https://ucicinemas.it/movies/dio-ride/acquista/5664/2968/45550',
        )

    def test_ov_slug_version_is_original_and_italian_slug_is_not(self):
        def version(slug, lang, subs):
            return {"slug": slug, "language": {"name": lang, "slug": lang},
                    "subtitles": {"name": subs} if subs else None,
                    "performances": [{"day": "2026-11-04", "actual_start_at": "20:00"}]}
        payload = {"data": [
            {"title": "Ov Film", "screens": [{"2D": [version("ov-ov-film", "EN", "ITA")]}]},
            {"title": "Plain Film", "screens": [{"2D": [version("plain-film", "ITA", None)]}]},
        ]}
        rows = {r['title']: r for r in cinema.parse_uci(payload, UCI_SOURCE, {})}
        self.assertEqual(rows['Ov Film']['classification'], 'original')
        self.assertEqual(rows['Plain Film']['classification'], 'unknown')

    def test_malformed_payload_does_not_raise(self):
        self.assertEqual(cinema.parse_uci({}, UCI_SOURCE, KNOWN), [])
        self.assertEqual(cinema.parse_uci({'data': None}, UCI_SOURCE, KNOWN), [])
        self.assertEqual(cinema.parse_uci({'data': ['x', None]}, UCI_SOURCE, KNOWN), [])


class SpaceParserTests(unittest.TestCase):
    def setUp(self):
        self.rows = cinema.parse_space(json.loads(SPACE_JSON), SPACE_SOURCE, KNOWN)
        self.by_title = {}
        for row in self.rows:
            self.by_title.setdefault(row['title'], []).append(row)

    def test_mixed_italian_and_vo_sessions_stay_separate(self):
        fast = self.by_title['FAST & FURIOUS - 25MO ANNIVERSARIO']
        self.assertEqual([row['time'] for row in fast], ['16:10', '18:20', '21:30', '18:50'])
        self.assertEqual([row['classification'] for row in fast],
                         ['unknown', 'unknown', 'unknown', 'original'])
        self.assertTrue(all(row['date'] == '2026-11-05' for row in fast))

    def test_italian_override_marks_italian_sessions(self):
        dio = self.by_title['DIO RIDE']
        self.assertEqual(len(dio), 2)
        self.assertTrue(all(row['classification'] == 'italian' for row in dio))

    def test_italiano_without_override_is_unknown_not_dubbed(self):
        english = self.by_title['English Film']
        self.assertEqual(len(english), 1)
        self.assertEqual(english[0]['classification'], 'unknown')
        self.assertNotIn('dubbed', {row['classification'] for row in self.rows})
        self.assertEqual(self.by_title['No Attributes'][0]['classification'], 'unknown')
        self.assertEqual(self.by_title['Unknown Language'][0]['classification'], 'unknown')

    def test_known_year_mismatch_rejects_the_italian_override(self):
        self.assertEqual(self.by_title['Italian Film'][0]['classification'], 'unknown')

    def test_source_and_booking_links(self):
        fast = self.by_title['FAST & FURIOUS - 25MO ANNIVERSARIO']
        vo = fast[-1]
        self.assertEqual(vo['sourceUrl'],
                         'https://www.thespacecinema.it/film/fast-and-furious')
        self.assertEqual(vo['bookingUrl'],
                         'https://www.thespacecinema.it/prenotare-il-biglietto/summary/1026/HO1/4')
        self.assertEqual(vo['cinemaId'], 'space')
        self.assertEqual(vo['driveMinutes'], 25)
        self.assertEqual(self.by_title['No Attributes'][0]['bookingUrl'],
                         'https://www.thespacecinema.it/film/no-attributes')

    def test_session_date_wins_over_the_group_date(self):
        row = self.by_title['Midnight'][0]
        self.assertEqual((row['date'], row['time']), ('2026-11-06', '00:15'))

    def test_malformed_rows_are_skipped_without_inventing_sessions(self):
        self.assertEqual(len(self.rows), 11)
        self.assertNotIn('', self.by_title)
        self.assertEqual(len(self.by_title['English Film']), 1)

    def test_film_without_groups_produces_no_rows(self):
        payload = {'result': [{'filmTitle': 'Empty'}]}
        self.assertEqual(cinema.parse_space(payload, SPACE_SOURCE, KNOWN), [])

    def test_api_shape_change_raises_instead_of_returning_zero_rows(self):
        for payload in ({}, {'result': None}, {'result': 'nope'}, [], 'x',
                        {'result': [{'filmTitle': 'Bad', 'showingGroups': 'nope'}]},
                        {'result': [{'filmTitle': 'Bad',
                                     'showingGroups': [{'sessions': 'nope'}]}]}):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    cinema.parse_space(payload, SPACE_SOURCE, KNOWN)

    def test_api_error_message_is_surfaced_verbatim(self):
        with self.assertRaisesRegex(ValueError, 'Token scaduto'):
            cinema.parse_space({'errorMessage': 'Token scaduto', 'result': None},
                               SPACE_SOURCE, KNOWN)


class ContractTests(unittest.TestCase):
    ROW_KEYS = {
        'id', 'title', 'cinemaId', 'cinema', 'city', 'date', 'time', 'language',
        'classification', 'evidence', 'sourceUrl', 'bookingUrl', 'driveMinutes',
        'languageCode', 'evidenceCode', 'evidenceParams', 'year',
    }

    def test_screening_row_has_every_contract_field(self):
        row = cinema.screening(TEST_SOURCE, 'Film', '2026-11-04', '18:00',
                               'versione originale', '', KNOWN)
        self.assertEqual(set(row), self.ROW_KEYS)
        self.assertEqual(row['cinemaId'], 'test')
        self.assertEqual(row['classification'], 'original')
        self.assertIsInstance(row['driveMinutes'], int)
        self.assertEqual(row['id'], cinema.screening(
            TEST_SOURCE, 'Film', '2026-11-04', '18:00', 'versione originale', '', KNOWN)['id'])

    def test_source_status_has_every_contract_field(self):
        status = cinema.source_statuses(now=datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc))[0]
        self.assertEqual(set(status), {
            'id', 'name', 'city', 'driveMinutes', 'url',
            'status', 'message', 'checkedAt', 'messageCode', 'messageParams',
        })
        self.assertEqual(status['checkedAt'], '2026-11-04T13:00:00+01:00')

    def test_manual_sources_are_manual_and_have_no_loader(self):
        statuses = {item['id']: item for item in cinema.source_statuses()}
        for source_id in ('massimo', 'santandrea'):
            self.assertEqual(statuses[source_id]['status'], 'manual')
            self.assertTrue(statuses[source_id]['message'])
            self.assertNotIn(source_id, cinema.LOADERS)
        source_ids = {item['id'] for item in cinema.SOURCES}
        self.assertTrue(set(cinema.LOADERS) <= source_ids)
        self.assertEqual(set(cinema.LOADERS), {'arca', 'universo', 'uci', 'space'})

    def test_space_source_uses_the_canonical_cinema_page(self):
        status = next(item for item in cinema.source_statuses() if item['id'] == 'space')
        self.assertEqual(status['url'],
                         'https://www.thespacecinema.it/cinema/montesilvano/al-cinema')
        self.assertEqual(status['driveMinutes'], 25)


class TranslationCodeTests(unittest.TestCase):
    """Every displayed backend message keeps its Italian text and adds a code."""

    def row(self, **kwargs):
        return cinema.screening(TEST_SOURCE, kwargs.pop('title', 'Sconosciuto'),
                                '2026-11-04', '18:00', kwargs.pop('label', ''),
                                known=KNOWN, **kwargs)

    def test_explicit_original_label_has_a_stable_code_and_params(self):
        row = self.row(label='VERSIONE ORIGINALE')
        self.assertEqual(row['languageCode'], 'language.original')
        self.assertEqual(row['evidenceCode'], 'evidence.original.label')
        self.assertEqual(row['evidenceParams'], {'label': 'versione originale'})
        self.assertEqual(row['language'], 'Versione originale')
        self.assertIn('versione originale', row['evidence'])

    def test_original_version_in_title_counts_when_session_has_no_language(self):
        # The Space special events: no language attribute, VO only in the title.
        for title in ('George Michael : the Faith Tour - Lingua Originale',
                      'Some Film (V.O.)', 'Some Film - VOS', 'Concerto in versione originale'):
            row = self.row(title=title)
            self.assertEqual(row['classification'], 'original', title)
            self.assertEqual(row['evidenceCode'], 'evidence.original.title')
            self.assertEqual(row['evidenceParams'], {'title': title})

    def test_title_short_tags_inside_words_do_not_count(self):
        for title in ('Vos amis', 'Il volo', 'Ovunque tu sia', 'Love Story'):
            self.assertEqual(self.row(title=title)['classification'], 'unknown', title)

    def test_dubbed_label_beats_original_title(self):
        row = self.row(title='Film - Lingua Originale', label='doppiato')
        self.assertEqual(row['classification'], 'dubbed')

    def test_italian_audio_beats_original_title(self):
        row = self.row(title='Film - Lingua Originale', audio_lang='italiano')
        self.assertEqual(row['classification'], 'unknown')

    def test_verified_original_language_has_a_language_code(self):
        row = self.row(title='English Film', audio_lang='ENG', year=2026)
        self.assertEqual(row['languageCode'], 'language.en')
        self.assertEqual(row['evidenceCode'], 'evidence.original.verified')
        self.assertEqual(row['evidenceParams'], {'language': 'en', 'titleOnly': False})
        self.assertEqual(row['language'], 'Inglese')

    def test_italian_metadata_code_keeps_the_curated_evidence_for_italian(self):
        row = self.row(title='Italian Film', year=2026)
        self.assertEqual(row['languageCode'], 'language.italian')
        self.assertEqual(row['evidenceCode'], 'evidence.italian.metadata')
        self.assertEqual(row['evidenceParams']['sourceEvidence'],
                         'Scheda film: lingua originale italiana.')
        self.assertFalse(row['evidenceParams']['titleOnly'])
        self.assertEqual(row['evidence'], 'Scheda film: lingua originale italiana.')

    def test_title_only_match_sets_the_param_instead_of_embedding_italian(self):
        row = self.row(title='Italian Film')
        self.assertEqual(row['evidenceCode'], 'evidence.italian.metadata')
        self.assertTrue(row['evidenceParams']['titleOnly'])
        self.assertIn('anno non disponibile', row['evidence'])

    def test_audio_mismatch_dubbed_code_carries_both_language_codes(self):
        row = self.row(title='English Film', audio_lang='ITA', year=2026)
        self.assertEqual(row['classification'], 'dubbed')
        self.assertEqual(row['languageCode'], 'language.dubbed')
        self.assertEqual(row['evidenceCode'], 'evidence.dubbed.audio')
        self.assertEqual(row['evidenceParams'], {'filmLanguage': 'en', 'audioLanguage': 'it'})

    def test_dubbed_label_code_keeps_the_label_for_italian(self):
        row = self.row(label='DOPPIATO')
        self.assertEqual(row['languageCode'], 'language.dubbed')
        self.assertEqual(row['evidenceCode'], 'evidence.dubbed.label')
        self.assertEqual(row['evidenceParams'], {'label': 'doppiato'})

    def test_unknown_audio_code_carries_the_language_code(self):
        row = self.row(audio_lang='KOR')
        self.assertEqual(row['languageCode'], 'language.unknown')
        self.assertEqual(row['evidenceCode'], 'evidence.unknown.audio')
        self.assertEqual(row['evidenceParams'], {'language': 'ko'})
        self.assertIn('Coreano', row['evidence'])

    def test_no_evidence_code_for_a_plain_unknown(self):
        row = self.row()
        self.assertEqual(row['languageCode'], 'language.unknown')
        self.assertEqual(row['evidenceCode'], 'evidence.unknown.none')
        self.assertEqual(row['evidenceParams'], {})

    def test_arca_daily_note_is_a_param_not_extra_italian_text(self):
        rows = cinema.parse_multicinema(ARCA_HTML, ARCA_SOURCE, '2026-11-04', {})
        fast = [row for row in rows if row['title'].startswith('Fast and Furious')]
        self.assertEqual(len(fast), 2)
        for row in fast:
            self.assertEqual(row['evidenceCode'], 'evidence.original.label')
            self.assertTrue(row['evidenceParams']['dailyNote'])
            self.assertIn('scheda giornaliera', row['evidence'])

    def test_manual_source_statuses_carry_their_message_codes(self):
        statuses = {item['id']: item for item in cinema.source_statuses()}
        self.assertEqual(statuses['massimo']['messageCode'], 'source.manual.generic')
        self.assertEqual(statuses['santandrea']['messageCode'], 'source.manual.cityplex')
        self.assertEqual(statuses['massimo']['messageParams'], {})
        self.assertIn('Cityplex', statuses['santandrea']['message'])

    def test_note_codes_are_parallel_to_the_italian_notes(self):
        original_loaders = cinema.LOADERS
        original_cache, original_at = cinema.CACHE, cinema.CACHE_AT
        try:
            cinema.LOADERS = {}
            data = cinema.gather(refresh=True)
        finally:
            cinema.LOADERS = original_loaders
            cinema.CACHE, cinema.CACHE_AT = original_cache, original_at
        self.assertEqual(len(data['notes']), 3)
        self.assertEqual(data['noteCodes'],
                         ['notes.dev', 'notes.drive', 'notes.sevenDays'])
        self.assertEqual(len(data['notes']), len(data['noteCodes']))
        self.assertTrue(all(isinstance(note, str) and note for note in data['notes']))


DATE_CLAIM = re.compile(
    r'settimanale|aggiornat|oggi|domani|questa settimana|prossim|fino al|'
    r'\b(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|'
    r'settembre|ottobre|novembre|dicembre)\b|'
    r'\b\d{1,2}\s*(?:°|º)?\s*(?:gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)\b|'
    r'\b\d{1,2}/\d{1,2}\b|\b20\d{2}\b',
    re.IGNORECASE,
)


class ManualSourceTests(unittest.TestCase):
    MANUAL_IDS = ('massimo', 'santandrea')

    def test_manual_messages_make_no_programme_or_date_claim(self):
        for source_id in self.MANUAL_IDS:
            with self.subTest(source_id):
                message = cinema.MANUAL_MESSAGES[source_id]
                self.assertIsNone(DATE_CLAIM.search(message), message)
                self.assertIn('verificare', message.casefold())

    def test_manual_sources_emit_no_rows_and_never_report_ok(self):
        original_loaders = cinema.LOADERS
        original_cache, original_at = cinema.CACHE, cinema.CACHE_AT
        try:
            cinema.LOADERS = {}
            data = cinema.gather(refresh=True)
        finally:
            cinema.LOADERS = original_loaders
            cinema.CACHE, cinema.CACHE_AT = original_cache, original_at
        self.assertEqual(data['screenings'], [])
        self.assertFalse(any(item['status'] == 'ok' for item in data['sources']))
        for source_id in self.MANUAL_IDS:
            status = next(item for item in data['sources'] if item['id'] == source_id)
            self.assertEqual(status['status'], 'manual')
            self.assertNotIn(source_id, cinema.LOADERS)


class SourceErrorTests(unittest.TestCase):
    def test_failing_loader_reports_error_with_the_exact_reason(self):
        original_loaders = cinema.LOADERS
        original_cache, original_at = cinema.CACHE, cinema.CACHE_AT

        def failing_loader(source, offset, known):
            raise RuntimeError('HTTP Error 503: Service Unavailable')

        try:
            cinema.LOADERS = {'space': failing_loader}
            data = cinema.gather(refresh=True)
        finally:
            cinema.LOADERS = original_loaders
            cinema.CACHE, cinema.CACHE_AT = original_cache, original_at
        status = next(item for item in data['sources'] if item['id'] == 'space')
        self.assertEqual(status['status'], 'error')
        self.assertEqual(status['messageCode'], 'source.error')
        self.assertEqual(status['messageParams'], {
            'days': 0, 'total': 7, 'reason': 'HTTP Error 503: Service Unavailable',
        })
        self.assertIn('0/7 giorni letti', status['message'])
        self.assertIn('HTTP Error 503', status['message'])
        self.assertEqual(data['screenings'], [])

    def test_successful_source_reports_ok_code_and_counts(self):
        original_loaders = cinema.LOADERS
        original_cache, original_at = cinema.CACHE, cinema.CACHE_AT

        def working_loader(source, offset, known):
            return []

        try:
            cinema.LOADERS = {'space': working_loader}
            data = cinema.gather(refresh=True)
        finally:
            cinema.LOADERS = original_loaders
            cinema.CACHE, cinema.CACHE_AT = original_cache, original_at
        status = next(item for item in data['sources'] if item['id'] == 'space')
        self.assertEqual(status['status'], 'ok')
        self.assertEqual(status['messageCode'], 'source.ok')
        self.assertEqual(status['messageParams'], {'days': 7, 'total': 7})
        self.assertEqual(status['message'], '7/7 giorni letti')


class HostValidationTests(unittest.TestCase):
    def test_loopback_hosts_are_allowed(self):
        self.assertTrue(cinema.host_allowed('127.0.0.1:8765', 8765))
        self.assertTrue(cinema.host_allowed('localhost:8765', 8765))
        self.assertTrue(cinema.host_allowed('LOCALHOST:8765', 8765))

    def test_other_hosts_are_rejected(self):
        for host in ('evil.example', '127.0.0.1:9999', 'localhost', '',
                     '127.0.0.1:8765.evil.example', None):
            with self.subTest(host=host):
                self.assertFalse(cinema.host_allowed(host, 8765))


class UrlValidationTests(unittest.TestCase):
    def test_http_url_accepts_only_http_and_https(self):
        self.assertEqual(cinema.http_url('https://example.com/a', 'https://fallback'),
                         'https://example.com/a')
        self.assertEqual(cinema.http_url('http://example.com/a', 'https://fallback'),
                         'http://example.com/a')
        for value in ('javascript:alert(1)', '//evil.example/x', 'https:///nohost',
                      'data:text/html,x', None):
            with self.subTest(value=value):
                self.assertEqual(cinema.http_url(value, 'https://fallback'), 'https://fallback')

    def test_screening_falls_back_to_the_source_url(self):
        row = cinema.screening(TEST_SOURCE, 'Film', '2026-11-04', '18:00',
                               '', 'javascript:alert(1)', KNOWN)
        self.assertEqual(row['bookingUrl'], TEST_SOURCE['url'])
        self.assertEqual(row['sourceUrl'], TEST_SOURCE['url'])
        kept = cinema.screening(TEST_SOURCE, 'Film', '2026-11-04', '18:00',
                                '', 'https://tickets.example/x', KNOWN)
        self.assertEqual(kept['bookingUrl'], 'https://tickets.example/x')


TMDB_SEARCH = '''
{
  "page": 1,
  "results": [
    {"id": 438631, "title": "Dune", "original_title": "Dune",
     "release_date": "2021-09-15", "vote_average": 7.786, "vote_count": 15891},
    {"id": 841, "title": "Dune", "original_title": "Dune",
     "release_date": "1984-12-14", "vote_average": 6.195, "vote_count": 3603},
    {"id": 881460, "title": "Planet Dune", "original_title": "Planet Dune",
     "release_date": "2021-10-29", "vote_average": 5.0, "vote_count": 73}
  ],
  "total_results": 3
}
'''

TMDB_DETAIL_IT = '''
{"id": 438631, "title": "Dune", "original_title": "Dune",
 "release_date": "2021-09-15",
 "overview": "Paul Atreides, un giovane brillante e dotato, deve recarsi sul pianeta piu pericoloso dell'universo.",
 "vote_average": 7.786, "vote_count": 15891}
'''

TMDB_DETAIL_EN = '''
{"id": 438631, "title": "Dune", "original_title": "Dune",
 "release_date": "2021-09-15",
 "overview": "Paul Atreides, a brilliant and gifted young man, must travel to the most dangerous planet in the universe.",
 "vote_average": 7.786, "vote_count": 15891}
'''

TMDB_DETAIL_IT_EMPTY = '''
{"id": 438631, "title": "Dune", "original_title": "Dune",
 "release_date": "2021-09-15", "overview": "",
 "vote_average": 7.786, "vote_count": 15891}
'''

TMDB_HUNGER_GAMES = '''
{"page": 1, "results": [
  {"id": 1024773,
   "title": "Hunger Games - La ballata dell'usignolo e del serpente",
   "original_title": "The Hunger Games: The Ballad of Songbirds & Snakes",
   "release_date": "2023-11-15", "vote_average": 7.0, "vote_count": 3776}
], "total_results": 1}
'''

TMDB_DETAIL_NO_VOTES = '''
{"id": 1024773,
 "title": "Hunger Games - La ballata dell'usignolo e del serpente",
 "original_title": "The Hunger Games: The Ballad of Songbirds & Snakes",
 "release_date": "2023-11-15", "overview": "Una trama.",
 "vote_average": 0.0, "vote_count": 0}
'''


class TmdbTests(unittest.TestCase):
    """Inline TMDB JSON only; every transport is a local function."""

    def payload(self, title='DUNE - Lingua originale', year=2021):
        return {'screenings': [{'title': title, 'year': year}]}

    def fixture(self, calls, search=TMDB_SEARCH, detail_it=TMDB_DETAIL_IT,
                detail_en=TMDB_DETAIL_EN):
        def send(url, headers):
            calls.append(url)
            self.assertEqual(headers['Authorization'], 'Bearer test-token')
            if '/search/movie' in url:
                return json.loads(search)
            if 'language=it-IT' in url:
                return json.loads(detail_it)
            return json.loads(detail_en)
        return send

    def test_clean_title_removes_original_language_suffixes_only(self):
        cases = {
            'FAST & FURIOUS - Lingua originale': 'FAST & FURIOUS',
            'Dune (VO)': 'Dune',
            'Dune (V.O.)': 'Dune',
            'Stray Kids … Lingua Originale': 'Stray Kids',
            'Rammstein – Lingua originale': 'Rammstein',
            'Hunger Games C.A.': 'Hunger Games',
            'Dune - Parte 2': 'Dune - Parte 2',
        }
        for raw, expected in cases.items():
            with self.subTest(raw):
                self.assertEqual(tmdb.clean_title(raw), expected)

    def test_normalize_title_folds_case_accents_and_spacing(self):
        self.assertEqual(tmdb.normalize_title('  Amélie  '),
                         tmdb.normalize_title('AMELIE'))
        self.assertNotEqual(tmdb.normalize_title('Fast & Furious'),
                            tmdb.normalize_title('Fast and Furious'))

    def test_exact_title_match_uses_the_year_to_pick_the_right_film(self):
        results = json.loads(TMDB_SEARCH)['results']
        match, reason = tmdb.select_match('Dune', results, 2021)
        self.assertEqual(match['id'], 438631)
        self.assertEqual(reason, 'exact')

    def test_known_year_mismatch_is_not_accepted(self):
        results = json.loads(TMDB_SEARCH)['results']
        match, reason = tmdb.select_match('Dune', results, 1990)
        self.assertIsNone(match)
        self.assertIn('year', reason)
        old_only = [item for item in results if item['release_date'].startswith('1984')]
        match, reason = tmdb.select_match('Dune', old_only, 2021)
        self.assertIsNone(match)
        self.assertIn('year', reason)
        no_date = [{'id': 11, 'title': 'Duna', 'original_title': 'Duna',
                    'vote_count': 100}]
        match, reason = tmdb.select_match('Dune', no_date, 2021)
        self.assertIsNone(match)
        self.assertIn('year', reason)

    def test_yearless_release_more_than_two_years_old_is_not_matched(self):
        calls = []
        payload = tmdb.enrich(self.payload('Hunger Games C.A.', year=None),
                              token='test-token', cache={}, cache_path=None,
                              overrides={},
                              transport=self.fixture(calls, search=TMDB_HUNGER_GAMES),
                              today=date(2026, 11, 5))
        self.assertEqual(payload['tmdb']['films'], {})
        self.assertNotIn('tmdbKey', payload['screenings'][0])
        self.assertIn('2 years', next(iter(payload['tmdb']['misses'].values())))
        self.assertTrue(any('query=Hunger+Games' in url for url in calls))

    def test_yearless_recent_release_is_still_matched(self):
        results = [{'id': 5, 'title': 'Dune', 'original_title': 'Dune',
                    'release_date': '2026-10-01', 'vote_count': 100}]
        match, reason = tmdb.select_match('Dune', results, today=date(2026, 11, 5))
        self.assertEqual(match['id'], 5)

    def test_dropping_old_results_does_not_create_a_single_result_match(self):
        results = [
            {'id': 1, 'title': 'Hunger Games', 'original_title': 'Hunger Games',
             'release_date': '2012-03-23', 'vote_count': 20000},
            {'id': 2, 'title': 'The Hunger Games: Sunrise on the Reaping',
             'original_title': 'The Hunger Games: Sunrise on the Reaping',
             'release_date': '2026-11-20', 'vote_count': 100},
        ]
        match, reason = tmdb.select_match('Hunger Games', results,
                                          today=date(2026, 11, 5))
        self.assertIsNone(match)
        self.assertIn('no exact', reason)

    def test_ambiguous_exact_titles_show_nothing(self):
        results = [
            {'id': 1, 'title': 'Dune', 'original_title': 'Dune',
             'release_date': '2021-01-01', 'vote_count': 100},
            {'id': 2, 'title': 'Dune', 'original_title': 'Dune',
             'release_date': '2021-06-01', 'vote_count': 100},
        ]
        match, reason = tmdb.select_match('Dune', results)
        self.assertIsNone(match)
        self.assertIn('ambig', reason)

        unrelated = [
            {'id': 3, 'title': 'Planet Dune', 'original_title': 'Planet Dune',
             'release_date': '2021-01-01', 'vote_count': 200},
            {'id': 4, 'title': 'Dune Drifter', 'original_title': 'Dune Drifter',
             'release_date': '2020-01-01', 'vote_count': 200},
        ]
        match, reason = tmdb.select_match('Dune', unrelated, 2021)
        self.assertIsNone(match)
        self.assertIn('no exact', reason)

    def test_single_unrelated_result_needs_the_minimum_vote_count(self):
        only = [{'id': 9, 'title': 'Duna', 'original_title': 'Duna',
                 'release_date': '2021-01-01', 'vote_count': 60}]
        match, reason = tmdb.select_match('Dune', only, 2021)
        self.assertEqual(match['id'], 9)
        self.assertEqual(reason, 'single result')
        low = [{'id': 10, 'title': 'Duna', 'original_title': 'Duna',
                'release_date': '2021-01-01', 'vote_count': 4}]
        match, reason = tmdb.select_match('Dune', low, 2021)
        self.assertIsNone(match)
        self.assertIn('votes', reason)

    def test_enrich_attaches_rating_and_both_plots(self):
        calls = []
        payload = tmdb.enrich(self.payload(), token='test-token', cache={},
                              cache_path=None, overrides={},
                              transport=self.fixture(calls))
        film = next(iter(payload['tmdb']['films'].values()))
        self.assertEqual(film['id'], 438631)
        self.assertEqual(film['title'], 'Dune')
        self.assertEqual(film['year'], 2021)
        self.assertEqual(film['rating'], 7.8)
        self.assertEqual(film['votes'], 15891)
        self.assertIn('Paul Atreides', film['overviewIt'])
        self.assertIn('Paul Atreides', film['overviewEn'])
        self.assertEqual(payload['screenings'][0]['tmdbKey'],
                         next(iter(payload['tmdb']['films'])))

    def test_empty_italian_plot_keeps_the_english_one(self):
        calls = []
        payload = tmdb.enrich(self.payload(), token='test-token', cache={},
                              cache_path=None, overrides={},
                              transport=self.fixture(calls, detail_it=TMDB_DETAIL_IT_EMPTY))
        film = next(iter(payload['tmdb']['films'].values()))
        self.assertEqual(film['overviewIt'], '')
        self.assertIn('Paul Atreides', film['overviewEn'])

    def test_zero_votes_hide_the_rating(self):
        calls = []
        payload = tmdb.enrich(self.payload(), token='test-token', cache={},
                              cache_path=None, overrides={},
                              transport=self.fixture(calls, detail_it=TMDB_DETAIL_NO_VOTES,
                                                     detail_en=TMDB_DETAIL_NO_VOTES))
        film = next(iter(payload['tmdb']['films'].values()))
        self.assertEqual(film['votes'], 0)
        self.assertIsNone(film['rating'])

    def test_override_id_skips_search(self):
        calls = []
        payload = tmdb.enrich(self.payload(), token='test-token', cache={},
                              cache_path=None, overrides={'dune': 841},
                              transport=self.fixture(calls))
        film = next(iter(payload['tmdb']['films'].values()))
        self.assertEqual(film['id'], 841)
        self.assertFalse(any('/search/movie' in url for url in calls))
        self.assertTrue(any('/movie/841' in url for url in calls))

    def test_null_override_blocks_the_match_without_a_request(self):
        calls = []
        payload = tmdb.enrich(self.payload(), token='test-token', cache={},
                              cache_path=None, overrides={'dune': None},
                              transport=self.fixture(calls))
        self.assertEqual(payload['tmdb']['films'], {})
        self.assertTrue(payload['tmdb']['misses'])
        self.assertEqual(calls, [])
        self.assertNotIn('tmdbKey', payload['screenings'][0])

    def test_missing_key_returns_the_payload_unchanged(self):
        calls = []
        payload = self.payload()
        result = tmdb.enrich(copy.deepcopy(payload), token=None,
                             key_path=tmdb.ROOT / 'missing-tmdb-key.txt',
                             cache={}, cache_path=None, overrides={},
                             transport=self.fixture(calls))
        self.assertEqual(result, payload)
        self.assertNotIn('tmdb', result)
        self.assertEqual(calls, [])

    def test_tmdb_failure_does_not_break_the_screenings(self):
        def broken(url, headers):
            raise tmdb.TmdbError('offline')
        payload = tmdb.enrich(self.payload(), token='test-token', cache={},
                              cache_path=None, overrides={}, transport=broken)
        self.assertEqual(payload['screenings'][0]['title'], 'DUNE - Lingua originale')
        self.assertEqual(payload['tmdb']['films'], {})
        self.assertIn('TMDB error', next(iter(payload['tmdb']['misses'].values())))

    def test_429_waits_and_retries_once(self):
        calls = []

        def send(url, headers):
            calls.append(url)
            if len(calls) == 1:
                raise tmdb.RateLimited(0)
            return json.loads(TMDB_SEARCH)

        client = tmdb.TmdbClient('test-token', transport=send,
                                 sleep=lambda seconds: None)
        results = client.search('Dune', 2021)
        self.assertEqual(len(calls), 2)
        self.assertEqual(results[0]['id'], 438631)

    def test_second_enrich_uses_the_memory_cache(self):
        cache = {}
        calls = []
        payload = self.payload()
        tmdb.enrich(copy.deepcopy(payload), token='test-token', cache=cache,
                    cache_path=None, overrides={}, transport=self.fixture(calls))
        first_calls = len(calls)
        self.assertGreater(first_calls, 0)

        def no_network(url, headers):
            raise AssertionError('network used on a cached film')

        second = tmdb.enrich(copy.deepcopy(payload), token='test-token', cache=cache,
                             cache_path=None, overrides={}, transport=no_network)
        self.assertEqual(len(calls), first_calls)
        self.assertTrue(second['tmdb']['films'])
        self.assertIn('tmdbKey', second['screenings'][0])


class TmdbGatherTests(unittest.TestCase):
    def test_gather_without_a_key_keeps_the_old_payload(self):
        original_path = cinema.TMDB_KEY_PATH
        original_loaders = cinema.LOADERS
        original_cache, original_at = cinema.CACHE, cinema.CACHE_AT
        try:
            cinema.TMDB_KEY_PATH = tmdb.ROOT / 'missing-tmdb-key.txt'

            def working_loader(source, offset, known):
                return [cinema.screening(source, 'Film', '2026-11-04', '18:00')]

            cinema.LOADERS = {'space': working_loader}
            data = cinema.gather(refresh=True)
        finally:
            cinema.TMDB_KEY_PATH = original_path
            cinema.LOADERS = original_loaders
            cinema.CACHE, cinema.CACHE_AT = original_cache, original_at
        self.assertEqual(len(data['screenings']), 1)
        self.assertNotIn('tmdb', data)


class DeployTests(unittest.TestCase):
    def test_token_from_env_wins_only_for_default_path(self):
        import os, tempfile
        from unittest import mock
        with mock.patch.dict(os.environ, {'TMDB_TOKEN': 'x' * 30}):
            self.assertEqual(tmdb.read_token(), 'x' * 30)
            with tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(tmdb.read_token(Path(tmp) / 'missing.txt'), '')

    def test_build_static_writes_site_without_key(self):
        import tempfile
        from unittest import mock
        data = {'updatedAt': 'x', 'screenings': [{'id': 'a'}], 'sources': [], 'notes': [], 'noteCodes': []}
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(cinema, 'gather', return_value=data):
            out = Path(tmp) / 'site'
            cinema.build_static(out)
            self.assertIn('data-static="1"', (out / 'index.html').read_text(encoding='utf-8'))
            self.assertEqual(json.loads((out / 'api' / 'screenings.json').read_text(encoding='utf-8')), data)
            self.assertFalse(any('tmdb' in p.name for p in out.rglob('*')))

    def test_build_static_refuses_empty_list(self):
        import tempfile
        from unittest import mock
        data = {'screenings': [], 'sources': []}
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(cinema, 'gather', return_value=data):
            with self.assertRaises(SystemExit):
                cinema.build_static(Path(tmp) / 'site')
            self.assertFalse((Path(tmp) / 'site').exists())


if __name__ == '__main__':
    unittest.main()
