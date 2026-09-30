"""Ingress-only installation help, available before the application can start."""
import html
import http.server
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

BASE = Path(__file__).parent
LANGUAGES = {'en': 'English', 'es': 'Español', 'fr': 'Français', 'de': 'Deutsch',
             'it': 'Italiano', 'pt': 'Português', 'nl': 'Nederlands', 'ru': 'Русский',
             'zh': '中文', 'ja': '日本語', 'ko': '한국어'}


def language(query, configured='en', accepted='en'):
    requested = parse_qs(query).get('lang', [''])[0]
    if requested in LANGUAGES:
        return requested
    if configured in LANGUAGES:
        return configured
    for part in accepted.split(','):
        candidate = part.split(';')[0].strip().split('-')[0].lower()
        if candidate in LANGUAGES:
            return candidate
    return 'en'


def render(state, locale='en'):
    locale = locale if locale in LANGUAGES else 'en'
    text = json.loads((BASE / 'locales' / (locale + '.json')).read_text(encoding='utf-8'))
    esc = lambda value: html.escape(str(value), quote=True)
    options = ''.join(f'<option value="{code}" {"selected" if code == locale else ""}>{name}</option>'
                      for code, name in LANGUAGES.items())
    steps = ''.join(f'<article><h2>{esc(text[title])}</h2><p>{esc(text[body])}</p></article>'
                    for title, body in [('step_domain', 'domain_help'), ('step_duck', 'duck_help'),
                                        ('step_certificate', 'certificate_help'), ('step_dns', 'dns_help'),
                                        ('step_finish', 'finish_help')])
    links = state.get('links', {})
    version_link = (f'<a href="{esc(links["source_url"])}" target="_blank" rel="noopener noreferrer">{esc(state.get("version", ""))}</a>'
                    if links.get('source_url') else '')
    navigation = ''.join(f'<a href="{esc(links[key])}" target="_blank" rel="noopener noreferrer">{esc(text[label])}</a>'
                         for key, label in [('source_url', 'source'), ('release_url', 'release'),
                                            ('wrapper_url', 'wrapper'), ('build_url', 'build')] if links.get(key))
    ready = state.get('ready') is True
    action = ''
    if ready:
        url = state.get('public_url', '')
        if urlsplit(url).scheme == 'https':
            action = f'<a class="button" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(text["open"])}</a>'
    gateway = ''
    if ready and state.get('gateway'):
        gateway = f'<p>{esc(text["gateway"])}</p><code class="secret">{esc(state["gateway"])}</code>'
    status = text['ready' if ready else 'failed' if state.get('error') else 'waiting']
    code = state.get('error', '')
    next_step = text['domain_help'] if code in ('CERT_HOSTNAME', 'CERT_SAN') else text['renew'] if code == 'CERT_EXPIRED' else text['certificate_help'] if code.startswith('CERT_') else text['restart']
    details = f'<details><summary>{esc(text["details"])}</summary><p><code>{esc(code or text["unknown"])}</code></p><p>{esc(text["restart"])}</p></details>'
    return f'''<!doctype html><html lang="{locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(text['title'])}</title>
<style>:root{{font-family:system-ui,sans-serif;color:#203137;background:#f3f7f6}}body{{margin:0}}main{{max-width:850px;margin:auto;padding:32px 22px}}header{{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}}h1{{font-size:clamp(1.8rem,4vw,2.7rem);margin:24px 0 10px}}h2{{font-size:1.15rem}}p{{line-height:1.75}}article,.status{{padding:20px 24px;border:1px solid #dce6e2;background:white;border-radius:15px;margin:16px 0}}.status{{border-left:5px solid #477e69}}.notice{{color:#68491d;background:#fff0d5;padding:14px;border-radius:10px}}a{{color:#216650}}.button{{display:inline-block;padding:12px 20px;border-radius:9px;background:#216650;color:white;text-decoration:none}}select,button{{font:inherit;padding:8px;border-radius:7px;border:1px solid #c7d6d0;background:white}}nav{{display:flex;gap:18px;flex-wrap:wrap;margin:28px 0}}code{{overflow-wrap:anywhere}}.secret{{display:block;user-select:all;background:#edf3ef;padding:12px;border-radius:8px}}details{{margin-top:20px}}footer{{font-size:.9rem}}:focus-visible{{outline:3px solid #df952e;outline-offset:3px}}</style></head><body><main>
<header><strong>Nocturne · {esc(state.get('channel', ''))} {version_link}</strong><form method="get"><label for="lang">{esc(text['language'])}</label> <select id="lang" name="lang">{options}</select> <button type="submit">{esc(text['language'])}</button></form></header>
<h1>{esc(text['title'])}</h1><p>{esc(text['intro'])}</p>
{'<p class="notice">'+esc(text['demo'])+'</p>' if state.get('demo') else ''}
<section class="status"><strong>{esc(status)}</strong><p>{esc(state.get('public_url', ''))}</p>{'<p>'+esc(next_step)+'</p>' if code else ''}{action}{gateway}</section>
<p>{esc(text['existing'])}</p>{steps}<article><p>{esc(text['renew'])}</p></article>{details}
<nav>{navigation}</nav><footer><a href="https://github.com/home-assistant/addons/blob/master/duckdns/DOCS.md" target="_blank" rel="noopener noreferrer">DuckDNS</a> · <a href="https://github.com/home-assistant/addons/blob/master/letsencrypt/DOCS.md" target="_blank" rel="noopener noreferrer">Let's Encrypt</a></footer>
</main></body></html>'''


def make_handler(state):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.client_address[0] != '172.30.32.2':
                self.send_error(403)
                return
            parsed = urlsplit(self.path)
            if parsed.path != '/':
                self.send_error(404)
                return
            locale = language(parsed.query, state.get('language', 'en'), self.headers.get('Accept-Language', 'en'))
            body = render(dict(state), locale).encode('utf-8')
            self.send_response(200)
            for name, value in [('Content-Type', 'text/html; charset=utf-8'), ('Cache-Control', 'no-store'),
                                ('Referrer-Policy', 'no-referrer'), ('X-Content-Type-Options', 'nosniff'),
                                ('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'"),
                                ('Content-Length', str(len(body)))]:
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass
    return Handler
