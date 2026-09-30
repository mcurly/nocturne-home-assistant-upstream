import http.server
import importlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'shared/rootfs/opt/nocturne-ha'))
sys.path.insert(0, str(BASE / 'tools'))
import help_ui
import run
from candidate import links, registry
from check_locales import check


class SetupTests(unittest.TestCase):
    def test_all_nocturne_languages_have_complete_rendered_help(self):
        check()
        for locale in help_ui.LANGUAGES:
            page = help_ui.render({'error': 'CERT_FILES'}, locale)
            self.assertIn(f'lang="{locale}"', page)
            self.assertIn('fullchain.pem', page)
            self.assertIn('privkey.pem', page)
            self.assertIn('CERT_FILES', page)
            self.assertNotIn('class="button"', page)

    def test_language_preference_and_browser_fallback(self):
        self.assertEqual(help_ui.language('lang=fr', 'nl', 'de-DE,en'), 'fr')
        self.assertEqual(help_ui.language('lang=invalid', 'auto', 'de-DE,en'), 'de')
        self.assertEqual(help_ui.language('', 'ja', 'nl'), 'ja')
        self.assertEqual(help_ui.language('', 'auto', 'xx'), 'en')

    def test_ready_state_and_html_escaping(self):
        page = help_ui.render({'ready': True, 'public_url': 'https://nocturne.example.net', 'gateway': '<script>bad</script>'})
        self.assertIn('class="button"', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertNotIn('<script>', page)
        self.assertNotIn('bad', help_ui.render({'ready': False, 'gateway': 'bad'}))

    def test_version_link_opens_upstream_tree_not_delivery_commit(self):
        result = links('a' * 40, 'v0.2.7', 'smokkelaar/nocturne-home-assistant-upstream', 'b' * 40, 123)
        self.assertEqual(result['source_url'], 'https://github.com/nightscout/nocturne/tree/' + 'a' * 40)
        self.assertIn('/releases/tag/v0.2.7', result['release_url'])
        self.assertIn('/tree/' + 'b' * 40 + '/deploy/home-assistant', result['wrapper_url'])

    def test_no_implicit_self_signed_certificate_in_production(self):
        with patch.dict('os.environ', {}, clear=True), tempfile.TemporaryDirectory() as tmp, patch.object(run, 'DATA', Path(tmp)):
            with self.assertRaisesRegex(ValueError, 'CERT_FILES'):
                run.prepare_tls({'certificate': '', 'hostname': 'example.net'})
            self.assertFalse((Path(tmp) / 'tls').exists())

    def test_direct_and_spoofed_ingress_clients_rejected(self):
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), help_ui.make_handler({'error': 'CERT_FILES'}))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = urllib.request.Request(f'http://127.0.0.1:{server.server_port}/', headers={'X-Forwarded-For': '172.30.32.2'})
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(request)
            self.assertEqual(caught.exception.code, 403)
        finally:
            server.shutdown()
            server.server_close()

    def test_allowed_ingress_gets_help_during_setup_failure(self):
        class AllowedHandler(help_ui.make_handler({'error': 'CERT_FILES'})):
            def setup(self):
                super().setup()
                self.client_address = ('172.30.32.2', 1234)
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), AllowedHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/?lang=nl') as response:
                page = response.read().decode('utf-8')
                self.assertIn('Nocturne installatiehulp', page)
                self.assertIn('CERT_FILES', page)
                self.assertEqual(response.headers['Cache-Control'], 'no-store')
        finally:
            server.shutdown()
            server.server_close()

    def test_wrong_platform_and_source_revision_refused(self):
        config = {'architecture': 'arm64', 'os': 'linux', 'config': {'Labels': {'org.opencontainers.image.revision': 'b' * 40}}}
        image = {'config': {'digest': 'sha256:config'}}
        with patch('candidate.fetch', side_effect=[({'token': 'synthetic'}, 't'), (image, 'm'), (config, 'sha256:config')]):
            with self.assertRaisesRegex(ValueError, 'platform'):
                registry('example/image', 'tag', 'amd64')
        with patch('candidate.fetch', side_effect=[({'token': 'synthetic'}, 't'), (image, 'm'), (config, 'sha256:config')]):
            with self.assertRaisesRegex(ValueError, 'revision'):
                registry('example/image', 'tag', 'arm64', 'a' * 40)


if __name__ == '__main__':
    unittest.main()
