"""Regression checks for documentation metadata; never starts the application."""
import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('public_docs',Path(__file__).with_name('check_public_docs.py'))
docs=importlib.util.module_from_spec(spec);spec.loader.exec_module(docs)
class PublicDocsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.previous=docs.ROOT;docs.ROOT=Path(self.temp.name)
        self.data={'repo':'Example','name':'Example','version':'1.0','platform':'macOS','tag':None,'status':'source','release_url':None,'source_url':'https://github.com/popovantondev/Example','help_url':'https://popovantondev.github.io/Example/Guide-{lang}.html','feedback_url':'https://github.com/popovantondev/Example/issues/new/choose','downloads':[],'assets':[],'checksums':[],'description':dict.fromkeys(docs.LANGS,'An application.'),'requirements':dict.fromkeys(docs.LANGS,'Source setup.'),'start':dict.fromkeys(docs.LANGS,'Read the guide.'),'version_files':[{'path':'VERSION','pattern':r'^(\S+)$'}]}
        (docs.ROOT/'VERSION').write_text('1.0')
        self.files={'README.md':docs.markdown(self.data,'en')}
        (docs.ROOT/'README.md').write_text(self.files['README.md'],encoding='utf-8')
    def tearDown(self):docs.ROOT=self.previous;self.temp.cleanup()
    def check(self):return docs.validate(self.data,self.files)
    def test_valid_metadata(self):self.assertEqual(self.check(),[])
    def test_summary_drift(self):
        (docs.ROOT/'README.md').write_text('changed');self.assertTrue(any('regenerate' in e for e in self.check()))
    def test_version_drift(self):
        (docs.ROOT/'VERSION').write_text('2.0');self.assertTrue(any('version mismatch' in e for e in self.check()))
    def test_raw_html_destination(self):
        self.data['help_url']='https://github.com/popovantondev/Example/blob/main/Guide-{lang}.html';self.assertTrue(any('published HTML' in e for e in self.check()))
    def test_source_only_download(self):
        self.data['downloads']=['app.zip'];self.assertTrue(any('source-only' in e for e in self.check()))
    def test_missing_image(self):
        (docs.ROOT/'README.md').write_text(self.files['README.md']+'\n![Example](missing.png)',encoding='utf-8');self.assertTrue(any('missing image' in e for e in self.check()))
    def test_missing_srcset_image(self):
        (docs.ROOT/'ok.png').write_bytes(b'x')
        picture='\n<picture><source media="(prefers-color-scheme: dark)" srcset="missing-dark.png"><img src="ok.png" alt="x"></picture>'
        (docs.ROOT/'README.md').write_text(self.files['README.md']+picture,encoding='utf-8');self.assertTrue(any('missing image missing-dark.png' in e for e in self.check()))
    def test_existing_srcset_image_passes(self):
        (docs.ROOT/'ok.png').write_bytes(b'x');(docs.ROOT/'dark.png').write_bytes(b'x')
        text=self.files['README.md']+'\n<picture><source media="(prefers-color-scheme: dark)" srcset="dark.png 1x, ok.png 2x"><img src="ok.png" alt="x"></picture>'
        self.files['README.md']=text;(docs.ROOT/'README.md').write_text(text,encoding='utf-8');self.assertEqual(self.check(),[])
    def test_missing_local_document(self):
        (docs.ROOT/'README.md').write_text(self.files['README.md']+'\n[Setup](missing.md)',encoding='utf-8');self.assertTrue(any('missing local link' in e for e in self.check()))
    def test_production_credit(self):
        (docs.ROOT/'README.md').write_text(self.files['README.md']+'\nCreated with ChatGPT',encoding='utf-8');self.assertTrue(any('production content' in e for e in self.check()))
    def test_functional_codex_reference_allowed(self):
        text=self.files['README.md']+'\nRuns approved tasks through Codex.';self.files['README.md']=text;(docs.ROOT/'README.md').write_text(text,encoding='utf-8');self.assertEqual(self.check(),[])
    def test_internal_instruction_file(self):
        (docs.ROOT/'AGENTS.md').write_text('Internal notes');self.assertTrue(any('Internal document' in e for e in self.check()))
    def test_missing_translation(self):
        del self.data['description']['ru'];self.assertTrue(any('incomplete localization' in e for e in self.check()))
    def test_release_tag_destination(self):
        self.data.update(tag='v1.0',release_url='https://github.com/popovantondev/Example/releases/latest',status='release');self.assertTrue(any('URL/tag mismatch' in e for e in self.check()))
class SharedDistributionTests(PublicDocsTests):
    def set_shared(self):
        release='https://github.com/popovantondev/Bundle/releases/tag/v2.0'
        self.data.update(status='preview',tag=None,release_url=release,shared_distribution={'repo':'Bundle','version':'2.0','tag':'v2.0','release_url':release,'application_versions':{'Example':'1.0'}})
    def test_shared_release_keeps_application_version(self):
        self.set_shared();self.assertEqual(self.check(),[]);self.assertEqual(docs.release_target(self.data),('Bundle','v2.0'))
    def test_unmarked_foreign_release_rejected(self):
        self.set_shared();del self.data['shared_distribution'];self.assertTrue(any('requires shared_distribution' in e for e in self.check()))
    def test_wrong_application_version_rejected(self):
        self.set_shared();self.data['shared_distribution']['application_versions']['Example']='2.0';self.assertTrue(any('application version mismatch' in e for e in self.check()))
    def test_shared_tag_cannot_be_own_tag(self):
        self.set_shared();self.data['tag']='v1.0';self.assertTrue(any('impersonate' in e for e in self.check()))
    def test_shared_asset_must_belong_to_declared_release(self):
        self.set_shared();self.data['assets']=[{'name':'setup.exe','url':'https://example.invalid/setup.exe'}];self.assertTrue(any('asset URL mismatch' in e for e in self.check()))
    def test_invalid_shared_repository_rejected(self):
        self.set_shared();self.data['shared_distribution']['repo']='../Other';self.assertTrue(any('invalid shared' in e for e in self.check()))

class ProfileReadmeTests(unittest.TestCase):
    """The profile README as GitHub shows it: demo cards, order, links and files."""
    def setUp(self):
        self.root=Path(__file__).resolve().parents[1]
        self.data=json.loads((self.root/'public-release.json').read_text(encoding='utf-8'))
    def test_piano_card_right_of_peakmp3_in_every_language(self):
        import re
        for l in docs.LANGS:
            text=docs.profile_readme(self.data,l)
            # Both demo cards sit in one paragraph (side by side; they wrap under each other on a phone): PeakMP3 first, the piano after it.
            row=re.search(r'<p>\n(<a href="[^"\n]*PeakMP3[^\n]*\n<a [^\n]*)\n</p>',text)
            self.assertIsNotNone(row,l)
            cells=row.group(1).split('\n')
            self.assertEqual(len(cells),2,l)
            self.assertIn('/PeakMP3/',cells[0]);self.assertTrue(cells[0].startswith('<a href="https://popovantondev.github.io/PeakMP3/'))
            self.assertIn('demo-peakmp3-'+l+'-light.',cells[0])
            self.assertTrue(cells[1].startswith('<a href="https://popovantondev.github.io/VirtualPianoArranger/play-'+l+'.html"'))
            self.assertIn('demo-piano-'+l+'-light.',cells[1])
            self.assertLess(text.index('demo-peakmp3-'),text.index('demo-piano-'))
            self.assertLess(text.index('demo-piano-'),text.index('card-'))
    def test_profile_pictures_are_light_dark_pairs_with_size_and_alt(self):
        import re
        for l in docs.LANGS:
            text=docs.profile_readme(self.data,l)
            pictures=re.findall(r'<picture>.*?</picture>',text)
            self.assertEqual(len(pictures),1+2+len(self.data['projects']),l)      # banner, two demos, one card per program
            for picture in pictures:
                self.assertRegex(picture,r'<source media="\(prefers-color-scheme: dark\)" srcset="https://raw\.githubusercontent\.com/popovantondev/popovantondev/main/docs/readme/[^"]+-'+l+r'-dark\.[0-9a-f]{8}\.webp">')
                self.assertRegex(picture,r'<img src="[^"]+-'+l+r'-light\.[0-9a-f]{8}\.webp" width="\d+" height="\d+" alt="[^"]{8,}">')
            self.assertNotIn('loading=',text)                                     # GitHub strips it, so it is not written
            self.assertNotIn('<table',text.split('<details>')[0])                 # no table above the text-only link list
    def test_profile_readme_uses_light_images_in_the_budget_of_the_brief(self):
        manifest=json.loads((self.root/'docs'/'readme'/'manifest.json').read_text(encoding='utf-8'))
        limits={'banner':50_000,'demo':15_000,'card':7_000}
        for image in manifest['images']:
            self.assertLessEqual((self.root/image['path']).stat().st_size,limits[image['kind'].split('-')[0]],image['path'])
        for l in docs.LANGS:
            for theme in ('light','dark'):
                total=sum(i['bytes'] for i in manifest['images'] if i['lang']==l and i['theme']==theme)
                self.assertLess(total,200*1000,(l,theme))
    def test_stale_banner_number_is_reported(self):
        import copy
        fewer=copy.deepcopy(self.data);fewer['projects']=fewer['projects'][:-1]
        errors=docs.validate(fewer,docs.generated(fewer))
        self.assertTrue(any('the banner shows 20 programs but the catalog has 19' in e for e in errors),errors)
    def test_profile_readmes_are_valid_and_current(self):
        files=docs.generated(self.data)
        self.assertEqual(docs.validate(self.data,files),[])
        for name,text in files.items():
            if name.startswith('README'):self.assertEqual((self.root/name).read_text(encoding='utf-8'),text,name)
class NetworkRetryTests(unittest.TestCase):
    def test_transient_connection_error_is_retried(self):
        import io
        from unittest.mock import patch
        with patch.object(docs.urllib.request, 'urlopen', side_effect=[ConnectionResetError('reset'), io.BytesIO(b'ok')]) as request, patch.object(docs.time, 'sleep'):
            self.assertEqual(docs.fetch_bytes('https://example.invalid'), b'ok')
            self.assertEqual(request.call_count, 2)

    def test_not_found_is_not_retried(self):
        from unittest.mock import patch
        error=docs.urllib.error.HTTPError('https://example.invalid', 404, 'Not found', {}, None)
        with patch.object(docs.urllib.request, 'urlopen', side_effect=error) as request, patch.object(docs.time, 'sleep'):
            with self.assertRaises(docs.urllib.error.HTTPError):
                docs.fetch_bytes('https://example.invalid')
            self.assertEqual(request.call_count, 1)

    def test_temporary_server_error_is_retried(self):
        import io
        from unittest.mock import patch
        error=docs.urllib.error.HTTPError('https://example.invalid', 503, 'Unavailable', {}, None)
        with patch.object(docs.urllib.request, 'urlopen', side_effect=[error, io.BytesIO(b'ok')]), patch.object(docs.time, 'sleep'):
            self.assertEqual(docs.fetch_bytes('https://example.invalid'), b'ok')

    def test_persistent_connection_error_still_fails(self):
        from unittest.mock import patch
        with patch.object(docs.urllib.request, 'urlopen', side_effect=ConnectionResetError('reset')) as request, patch.object(docs.time, 'sleep'):
            with self.assertRaises(ConnectionResetError):
                docs.fetch_bytes('https://example.invalid')
            self.assertEqual(request.call_count, 3)

if __name__=='__main__':unittest.main()
