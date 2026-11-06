#!/usr/bin/env python3
"""Offline checks for the shared kit: sync_kit.py, kit_programs.py and static kit properties."""
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
KIT = ROOT / 'assets' / 'kit'
KIT_FILES = ('kit.css', 'kit-theme.js', 'kit.js', 'programs.js', 'KIT_VERSION')


def run(script, *args):
    p = subprocess.run([sys.executable, '-X', 'utf8', str(TOOLS / script), *map(str, args)],
                       capture_output=True, text=True, encoding='utf-8')
    return p.returncode, p.stdout + p.stderr


def make_source(base, marker='a'):
    src = pathlib.Path(base) / 'src'
    src.mkdir()
    for name in KIT_FILES:
        (src / name).write_bytes(('/* %s %s */\n' % (name, marker)).encode('utf-8'))
    return src


class SyncKitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = pathlib.Path(self.tmp.name)
        self.src = make_source(self.base)

    def site(self, name):
        p = self.base / name
        p.mkdir()
        return p

    def test_to_copies_every_kit_file_byte_for_byte(self):
        site = self.site('siteA')
        code, out = run('sync_kit.py', '--source', self.src, '--to', site)
        self.assertEqual(code, 0, out)
        for name in KIT_FILES:
            self.assertEqual((site / 'assets' / 'kit' / name).read_bytes(), (self.src / name).read_bytes(), name)

    def test_check_passes_for_identical_copy(self):
        site = self.site('siteA')
        run('sync_kit.py', '--source', self.src, '--to', site)
        code, out = run('sync_kit.py', '--source', self.src, '--check', site)
        self.assertEqual(code, 0, out)

    def test_check_names_the_changed_file(self):
        site = self.site('siteA')
        run('sync_kit.py', '--source', self.src, '--to', site)
        (site / 'assets' / 'kit' / 'kit.css').write_bytes(b'/* edited */\n')
        code, out = run('sync_kit.py', '--source', self.src, '--check', site)
        self.assertEqual(code, 1, out)
        self.assertIn('kit.css', out)
        self.assertNotIn('kit.js', out)

    def test_check_reports_missing_kit(self):
        site = self.site('empty')
        code, out = run('sync_kit.py', '--source', self.src, '--check', site)
        self.assertEqual(code, 1, out)
        self.assertIn('empty', out)

    def test_check_lists_only_diverged_sites(self):
        good, bad = self.site('good'), self.site('bad')
        run('sync_kit.py', '--source', self.src, '--to', good, bad)
        (bad / 'assets' / 'kit' / 'kit-theme.js').write_bytes(b'x')
        code, out = run('sync_kit.py', '--source', self.src, '--check', good, bad)
        self.assertEqual(code, 1, out)
        self.assertIn('bad', out)
        self.assertNotIn('good', out)

    def test_check_flags_leftover_file(self):
        site = self.site('siteA')
        run('sync_kit.py', '--source', self.src, '--to', site)
        (site / 'assets' / 'kit' / 'old.css').write_bytes(b'')
        code, out = run('sync_kit.py', '--source', self.src, '--check', site)
        self.assertEqual(code, 1, out)
        self.assertIn('old.css', out)


FIXTURE = {
    'schema_version': 1, 'repo': 'popovantondev',
    'projects': [
        {'repo': 'Alpha', 'name': 'Alpha App', 'platform': 'macOS 13+ · Apple Silicon',
         'description': {'ru': 'Альфа', 'de': 'Alpha DE', 'en': 'Alpha EN'}},
        {'repo': 'Beta-Tool', 'name': 'Beta Tool', 'platform': 'Windows · x64',
         'description': {'ru': 'Бета', 'de': 'Beta DE', 'en': 'Beta EN'}},
    ],
    'catalog_icons': {'Alpha': 'assets/app-icons/Alpha.png', 'Beta-Tool': 'assets/app-icons/Beta-Tool.svg'},
    'catalog_categories': {'Alpha': 'lernen', 'Beta-Tool': 'daten'},
    'catalog_stacks': {'Alpha': 'Swift · SwiftUI', 'Beta-Tool': 'C# · .NET'},
    'catalog_websites': {
        'Alpha': {'ru': 'https://popovantondev.github.io/Alpha/index-ru.html',
                  'de': 'https://popovantondev.github.io/Alpha/index.html',
                  'en': 'https://popovantondev.github.io/Alpha/index-en.html'},
        'Beta-Tool': {'ru': 'https://popovantondev.github.io/Beta-Tool/index-ru.html',
                      'de': 'https://popovantondev.github.io/Beta-Tool/index.html',
                      'en': 'https://popovantondev.github.io/Beta-Tool/index-en.html'},
    },
}


def read_programs(path):
    text = pathlib.Path(path).read_text(encoding='utf-8')
    m = re.search(r'window\.PPK_PROGRAMS\s*=\s*(\[.*?\]);\s*\n', text, re.S)
    return json.loads(m.group(1)), text


class KitProgramsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        (self.root / 'assets' / 'kit').mkdir(parents=True)
        self.write_json(FIXTURE)

    def write_json(self, data):
        (self.root / 'public-release.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    def test_write_produces_contract_entries_in_catalog_order(self):
        code, out = run('kit_programs.py', '--root', self.root, '--write')
        self.assertEqual(code, 0, out)
        items, text = read_programs(self.root / 'assets' / 'kit' / 'programs.js')
        self.assertEqual([i['repo'] for i in items], ['Alpha', 'Beta-Tool'])
        self.assertEqual(items[0], {
            'repo': 'Alpha', 'name': 'Alpha App',
            'icon': 'https://popovantondev.github.io/popovantondev/assets/app-icons/Alpha.png',
            'category': 'lernen', 'stack': 'Swift · SwiftUI', 'platform': 'macOS 13+ · Apple Silicon',
            'url': {'de': 'https://popovantondev.github.io/Alpha/index.html',
                    'en': 'https://popovantondev.github.io/Alpha/index-en.html',
                    'ru': 'https://popovantondev.github.io/Alpha/index-ru.html'},
            'desc': {'de': 'Alpha DE', 'en': 'Alpha EN', 'ru': 'Альфа'}})
        self.assertIn('window.PPK_CATALOG', text)
        self.assertIn('https://popovantondev.github.io/popovantondev/index-en.html', text)
        self.assertIn('window.PPK_CATEGORIES', text)
        self.assertIn('"Daten & Backup"', text)
        self.assertNotIn('version', text.lower())

    def test_check_passes_after_write_and_fails_when_stale(self):
        run('kit_programs.py', '--root', self.root, '--write')
        self.assertEqual(run('kit_programs.py', '--root', self.root)[0], 0)
        data = json.loads(json.dumps(FIXTURE))
        data['projects'][0]['name'] = 'Alpha Renamed'
        self.write_json(data)
        code, out = run('kit_programs.py', '--root', self.root)
        self.assertEqual(code, 1, out)
        self.assertIn('programs.js', out)

    def test_missing_category_is_an_error_naming_the_repo(self):
        data = json.loads(json.dumps(FIXTURE))
        del data['catalog_categories']['Beta-Tool']
        self.write_json(data)
        code, out = run('kit_programs.py', '--root', self.root, '--write')
        self.assertEqual(code, 1, out)
        self.assertIn('Beta-Tool', out)

    def test_unknown_category_is_an_error(self):
        data = json.loads(json.dumps(FIXTURE))
        data['catalog_categories']['Alpha'] = 'games'
        self.write_json(data)
        code, out = run('kit_programs.py', '--root', self.root, '--write')
        self.assertEqual(code, 1, out)
        self.assertIn('Alpha', out)


class RealProfileDataTests(unittest.TestCase):
    def test_all_twenty_programs_with_category_stack_and_urls(self):
        d = json.loads((ROOT / 'public-release.json').read_text(encoding='utf-8'))
        items, _ = read_programs(KIT / 'programs.js')
        self.assertEqual([i['repo'] for i in items], [p['repo'] for p in d['projects']])
        self.assertEqual(len(items), 20)
        self.assertIn('VirtualPianoArranger', [i['repo'] for i in items])
        for i in items:
            self.assertIn(i['category'], ('lernen', 'medien', 'werkzeuge', 'daten'), i['repo'])
            self.assertTrue(i['stack'].strip(), i['repo'])
            for lang in ('de', 'en', 'ru'):
                self.assertTrue(i['url'][lang].startswith('https://popovantondev.github.io/'), i['repo'])
                self.assertTrue(i['desc'][lang].strip(), i['repo'])

    def test_program_sites_use_new_language_file_names(self):
        d = json.loads((ROOT / 'public-release.json').read_text(encoding='utf-8'))
        for repo, urls in d['catalog_websites'].items():
            if repo == 'VirtualPianoArranger':
                continue
            base = 'https://popovantondev.github.io/%s/' % repo
            self.assertEqual(urls, {'de': base + 'index.html', 'en': base + 'index-en.html', 'ru': base + 'index-ru.html'}, repo)

    def test_committed_programs_js_is_current(self):
        code, out = run('kit_programs.py')
        self.assertEqual(code, 0, out)


def luminance(hex_color):
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    chan = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255
        chan.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def token_block(css, opener):
    start = css.index(opener) + len(opener)
    return dict(re.findall(r'--ppk-([\w-]+)\s*:\s*([^;}]+)', css[start:css.index('}', start)]))


PAIRS = (('ink', 'bg'), ('ink', 'panel'), ('ink', 'tint'), ('muted', 'bg'), ('muted', 'panel'), ('muted', 'tint'),
         ('accent', 'bg'), ('accent', 'panel'), ('accent', 'tint'), ('accent-ink', 'accent'),
         ('term-ink', 'term'), ('term-ps', 'term'), ('term-ok', 'term'), ('term-dim', 'term'),
         ('ok', 'panel'), ('ok', 'bg'), ('ok-fg', 'ok-bg'), ('warn-fg', 'warn-bg'))


class KitStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (KIT / 'kit.css').read_text(encoding='utf-8')
        cls.js = (KIT / 'kit.js').read_text(encoding='utf-8')

    def test_text_contrast_is_at_least_4_5_in_both_themes(self):
        light = token_block(self.css, ':where(:root){')
        dark = token_block(self.css, ':where([data-theme="dark"]){')
        for theme, tokens in (('light', light), ('dark', dark)):
            merged = dict(light)
            merged.update(tokens)
            for fg, bg in PAIRS:
                ratio = contrast(merged[fg], merged[bg])
                self.assertGreaterEqual(ratio, 4.5, '%s: %s on %s = %.2f' % (theme, fg, bg, ratio))

    def test_system_dark_fallback_matches_explicit_dark_tokens(self):
        explicit = token_block(self.css, ':where([data-theme="dark"]){')
        media = token_block(self.css, '@media (prefers-color-scheme:dark){:where(:root:not([data-theme])){')
        self.assertEqual(media, explicit)

    def test_every_css_class_and_variable_is_prefixed(self):
        css = re.sub(r'/\*.*?\*/', '', self.css, flags=re.S)
        css = re.sub(r'url\("[^"]*"\)', 'url()', css)
        css = re.sub(r'"[^"]*"', '""', css)
        classes = set(re.findall(r'\.([A-Za-z_][\w-]*)', css))
        self.assertEqual({c for c in classes if not c.startswith('ppk-')}, set())
        variables = set(re.findall(r'(?<![\w-])--([\w-]+)\s*:', css))
        self.assertEqual({v for v in variables if not v.startswith('ppk-')}, set())

    def test_no_external_resources_and_no_ads(self):
        for name, text in (('kit.css', self.css), ('kit.js', self.js)):
            text = text.replace("xmlns='http://www.w3.org/2000/svg'", '')  # SVG namespace inside data: icons, not a request
            for url in re.findall(r'https?://[^\s"\')]+', text):
                self.assertTrue(url.startswith('https://popovantondev.github.io'), '%s: %s' % (name, url))
            self.assertNotRegex(text, r'(?i)@import|marquee|og:image|googletagmanager|analytics', name)

    def test_storage_key_and_version_format(self):
        self.assertIn("'ppk-theme'", (KIT / 'kit-theme.js').read_text(encoding='utf-8'))
        self.assertIn("'ppk-theme'", self.js)
        self.assertRegex((KIT / 'KIT_VERSION').read_text(encoding='utf-8'), r'^\d{4}\.\d{2}\.\d{2}-\d+\n$')

    def rules(self, needle):
        """Declaration bodies of every rule whose selector contains `needle` (media blocks included)."""
        css = re.sub(r'/\*.*?\*/', '', self.css, flags=re.S)
        css = re.sub(r'url\("[^"]*"\)', 'url()', css)
        return [body for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css) if needle in sel]

    def test_floating_header_does_not_animate_layout_properties(self):
        # Animating max-width/padding re-lays the page out on every frame; with backdrop-filter this made the
        # header "freeze" on the way into the pill. Only paint/composite properties may transition.
        banned = re.compile(r'\b(all|max-width|min-width|width|height|padding[\w-]*|margin[\w-]*|top|left|right|bottom|gap|flex[\w-]*|backdrop-filter)\b')
        checked = 0
        for needle in ('.ppk-nav-wrap', '.ppk-nav', '.ppk-floating'):
            for body in self.rules(needle):
                for prop in re.findall(r'(?<![\w-])transition(?:-property)?\s*:\s*([^;]+)', body):
                    checked += 1
                    names = re.sub(r'cubic-bezier\([^)]*\)', '', prop)
                    self.assertIsNone(banned.search(names), 'layout property transitions in the header: ' + prop)
        self.assertGreater(checked, 0)
        glass = ' '.join(self.rules('.ppk-nav::before'))
        self.assertIn('backdrop-filter', glass)  # the glass lives on its own fading layer
        self.assertRegex(' '.join(self.rules('.ppk-floating .ppk-nav::before')), r'opacity\s*:\s*1')
        for body in self.rules('.ppk-floating .ppk-nav'):
            if 'max-width' in body:  # the pill itself carries no glass: it would be repainted with the layout jump
                self.assertNotIn('backdrop-filter', body)

    def test_side_decor_is_one_fixed_quiet_layer_on_wide_screens_only(self):
        # Decor in the margins: a single fixed layer (no per-scroll painting), invisible to people and to the pointer,
        # shown only from 1280 px and built by script after load (nothing without JS, nothing on a phone).
        self.assertRegex(self.css, r'\n\.ppk-decor\{display:none\}')
        wide = re.search(r'@media \(min-width:1280px\)\{(.*?)\n\}', self.css, flags=re.S)
        self.assertIsNotNone(wide, 'decor is not gated to min-width:1280px')
        layer = re.search(r'\.ppk-decor\{([^{}]*)\}', wide.group(1)).group(1)
        for needle in ('position:fixed', 'pointer-events:none', 'z-index:0'):
            self.assertIn(needle, layer)
        for body in self.rules('.ppk-decor-i'):
            opacity = re.search(r'opacity\s*:\s*([\d.]+)', body)
            if opacity:
                self.assertLessEqual(float(opacity.group(1)), 0.25)
        self.assertRegex(self.css, r'@media \(prefers-reduced-motion:reduce\)\{[^@]*\.ppk-decor-side\{animation:none')
        self.assertNotRegex(' '.join(self.rules('.ppk-decor')), r'transition\s*:[^;]*\b(width|height|top|left|margin|padding)\b')
        self.assertRegex(self.js, r"'ppk-decor'\);\s*layer\.setAttribute\('aria-hidden', 'true'\)")
        self.assertIn('(min-width: 1280px)', self.js)
        decor_js = self.js[self.js.index('side decor'):self.js.index('function init()')]
        self.assertNotIn("'scroll'", decor_js)  # no scroll handler: the layer never repaints on scroll
        self.assertIn('data-ppk-slash', decor_js)  # the piano game page keeps its own note background
    def test_brand_label_is_not_clipped_in_the_floating_pill(self):
        # `overflow:hidden` on the label cut the last letter ("popovantondev" lost its v) and the descender of "p"
        # at fractional zoom (125/150 %). The label needs ink room on the right and below, paid back by negative margins.
        bodies = [b for b in self.rules('.ppk-brand span') if 'overflow' in b]
        self.assertEqual(len(bodies), 1)
        pad = re.search(r'padding\s*:\s*(\d+)px\s+(\d+)px\s+(\d+)px\s+0\b', bodies[0])
        mar = re.search(r'margin\s*:\s*-(\d+)px\s+-(\d+)px\s+-(\d+)px\s+0\b', bodies[0])
        self.assertTrue(pad and mar, bodies[0])
        self.assertGreaterEqual(int(pad.group(2)), 3)  # right
        self.assertGreaterEqual(int(pad.group(3)), 2)  # bottom (descenders)
        self.assertEqual(pad.groups(), mar.groups())


if __name__ == '__main__':
    unittest.main()
