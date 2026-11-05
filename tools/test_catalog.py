"""Tests for the profile catalog and README generation (German root, category tabs, links).

Reads the real public-release.json, so it belongs to the profile repository only.
Run: python -X utf8 tools/test_catalog.py
"""
import importlib.util
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_public_docs', ROOT / 'tools' / 'check_public_docs.py')
docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(docs)


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def tags(html):
    parser = Tags()
    parser.feed(html)
    return parser.tags


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'public-release.json').read_text(encoding='utf-8'))
        cls.files = docs.generated(cls.data)

    def test_german_is_the_root_language(self):
        self.assertEqual(
            set(self.files),
            {'index.html', 'index-en.html', 'index-ru.html', 'index-de.html',
             'README.md', 'README.en.md', 'README.ru.md'})
        for name, lang in (('index.html', 'de'), ('index-en.html', 'en'), ('index-ru.html', 'ru')):
            self.assertIn('<html lang="%s"' % lang, self.files[name])

    def test_old_german_catalog_name_redirects_to_the_root(self):
        text = self.files['index-de.html']
        self.assertIn('<meta http-equiv="refresh" content="0; url=index.html">', text)
        self.assertIn('<link rel="canonical" href="https://popovantondev.github.io/popovantondev/index.html">', text)
        self.assertIn('<a href="index.html">', text)

    def test_every_card_carries_the_category_from_the_data(self):
        for name in ('index.html', 'index-en.html', 'index-ru.html'):
            cards = {a['id']: a.get('data-category') for t, a in tags(self.files[name]) if t == 'article' and 'id' in a}
            self.assertEqual(cards, self.data['catalog_categories'], name)

    def test_tabs_start_on_all_and_cover_the_four_categories(self):
        for name in ('index.html', 'index-en.html', 'index-ru.html'):
            tabs = [a for t, a in tags(self.files[name]) if t == 'button' and a.get('role') == 'tab']
            self.assertEqual([a['data-category'] for a in tabs], ['all', 'lernen', 'medien', 'werkzeuge', 'daten'], name)
            self.assertEqual([a['aria-selected'] for a in tabs], ['true', 'false', 'false', 'false', 'false'], name)
        self.assertIn('>Daten &amp; Backup<', self.files['index.html'])

    def test_catalog_footer_has_impressum_and_datenschutz(self):
        for name in ('index.html', 'index-en.html', 'index-ru.html'):
            footer = self.files[name].split('<footer', 1)[1]
            self.assertIn('href="impressum.html"', footer, name)
            self.assertIn('href="datenschutz.html"', footer, name)

    def test_nothing_generated_links_to_an_about_page(self):
        for name, text in self.files.items():
            self.assertNotRegex(text, r'(?i)(href=["\']|\]\()[^"\')]*about', name)

    def test_readme_featured_contains_kartoteka_and_stays_even(self):
        text = self.files['README.md']
        featured = text.split('## Ausgewählte Anwendungen', 1)[1].split('## Alle Anwendungen', 1)[0]
        self.assertIn('<h3><a href="https://popovantondev.github.io/Kartoteka/index.html">Kartoteka</a></h3>', featured)
        self.assertEqual(featured.count('<td '), 8)

    def test_readme_table_names_open_the_program_site_and_source_is_separate(self):
        for name, lang in (('README.md', 'de'), ('README.en.md', 'en'), ('README.ru.md', 'ru')):
            table = self.files[name].split('|---|---|---|', 1)[1].split('##', 1)[0]
            for p in self.data['projects']:
                site = self.data['catalog_websites'][p['repo']][lang]
                row = next(r for r in table.splitlines() if r.startswith('| [%s](' % p['name']))
                self.assertTrue(row.startswith('| [%s](%s)' % (p['name'], site)), (name, p['repo']))
                self.assertIn('(%s)' % p['source_url'], row, (name, p['repo']))

    def test_german_readme_uses_sie(self):
        text = self.files['README.md']
        self.assertNotRegex(text, r'\b(Lade|Gib|nutze|dein\w*|dich|dir)\b')
        self.assertIn('Laden Sie', text)

    def test_built_with_keeps_javascript_linked_to_quick_answer(self):
        quick = self.data['catalog_websites']['QuickAnswer']
        for name, lang in (('README.md', 'de'), ('README.en.md', 'en'), ('README.ru.md', 'ru')):
            tail = self.files[name].rsplit('\n### ', 1)[1]
            self.assertIn('[JavaScript — Quick Answer](%s)' % quick[lang], tail, name)

    def test_readme_language_switcher_uses_the_new_names(self):
        for name in ('README.md', 'README.en.md', 'README.ru.md'):
            first = self.files[name].splitlines()[0]
            self.assertIn('<a href="README.md">Deutsch</a>', first)
            self.assertIn('<a href="README.en.md">English</a>', first)
            self.assertIn('<a href="README.ru.md">Русский</a>', first)

    def test_generated_pages_validate_against_the_files_on_disk(self):
        errors = docs.validate(self.data, self.files)
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
