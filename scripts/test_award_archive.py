import copy
import json
import unittest
from pathlib import Path

from award_archive import load_archive, validate_archive, render_archive, search_entries

ROOT = Path(__file__).resolve().parents[1]


class AwardArchiveTests(unittest.TestCase):
    def setUp(self):
        self.data = load_archive(ROOT / 'data' / 'awards.json')

    def test_duplicate_award_and_dangling_credit_rejected(self):
        data = copy.deepcopy(self.data)
        data['awards'].append(data['awards'][0])
        with self.assertRaises(ValueError):
            validate_archive(data)
        data = copy.deepcopy(self.data)
        data['awards'][0]['contributors'] = ['missing-person']
        with self.assertRaises(ValueError):
            validate_archive(data)

    def test_provenance_required_and_executable_urls_rejected(self):
        for key, value in [('source_url', 'javascript:alert(1)'), ('checked_at', 'bad-date'), ('evidence', 'world-champion')]:
            data = copy.deepcopy(self.data)
            data['awards'][0][key] = value
            with self.assertRaises(ValueError):
                validate_archive(data)

    def test_ny_edition_is_2025_not_article_publication_year(self):
        records = [a for a in self.data['awards'] if a['competition'] == 'high-times-ny']
        self.assertEqual({a['year'] for a in records}, {2025})

    def test_award_names_are_escaped_and_unmatched_cultivars_are_not_guessed(self):
        data = copy.deepcopy(self.data)
        data['awards'][0]['cultivar'] = '<script>alert(1)</script>'
        body = render_archive(data, {})
        self.assertIn('&lt;script&gt;', body)
        self.assertNotIn('<script>alert(1)</script>', body)
        self.assertNotIn('/cultivars/unknown', body)

    def test_search_indexes_cup_year_entrant_and_cultivar(self):
        entries = search_entries(self.data)
        entry = next(e for e in entries if e['name'] == 'White Widow' and '2025' in e['blurb'])
        self.assertIn('Doobie Labs', entry['blurb'])
        self.assertIn('High Times', entry['blurb'])
        self.assertTrue(entry['href'].startswith('/cups.html#'))

    def test_images_require_license_and_attribution(self):
        data = copy.deepcopy(self.data)
        data['awards'][0]['image'] = {'url': 'https://example.com/photo.jpg'}
        with self.assertRaises(ValueError):
            validate_archive(data)


if __name__ == '__main__':
    unittest.main()
