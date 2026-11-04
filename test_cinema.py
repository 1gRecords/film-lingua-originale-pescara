"""Offline tests for the cinema backend.

Every fixture is inline. Nothing in this module opens a socket, so the suite
also proves that the parsers do not depend on the live sites.
"""
import json
import unittest
from datetime import datetime, timezone

import cinema


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

    def test_malformed_payload_does_not_raise(self):
        self.assertEqual(cinema.parse_uci({}, UCI_SOURCE, KNOWN), [])
        self.assertEqual(cinema.parse_uci({'data': None}, UCI_SOURCE, KNOWN), [])
        self.assertEqual(cinema.parse_uci({'data': ['x', None]}, UCI_SOURCE, KNOWN), [])


class ContractTests(unittest.TestCase):
    ROW_KEYS = {
        'id', 'title', 'cinemaId', 'cinema', 'city', 'date', 'time', 'language',
        'classification', 'evidence', 'sourceUrl', 'bookingUrl', 'driveMinutes',
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
            'status', 'message', 'checkedAt',
        })
        self.assertEqual(status['checkedAt'], '2026-11-04T13:00:00+01:00')

    def test_manual_sources_are_manual_and_have_no_loader(self):
        statuses = {item['id']: item for item in cinema.source_statuses()}
        for source_id in ('massimo', 'santandrea', 'space'):
            self.assertEqual(statuses[source_id]['status'], 'manual')
            self.assertTrue(statuses[source_id]['message'])
            self.assertNotIn(source_id, cinema.LOADERS)
        source_ids = {item['id'] for item in cinema.SOURCES}
        self.assertTrue(set(cinema.LOADERS) <= source_ids)
        self.assertEqual(set(cinema.LOADERS), {'arca', 'universo', 'uci'})


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


if __name__ == '__main__':
    unittest.main()
