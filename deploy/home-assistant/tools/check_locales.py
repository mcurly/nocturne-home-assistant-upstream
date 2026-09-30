"""Fail on missing translations or drift from Nocturne's language list."""
import argparse
import json
from pathlib import Path
import urllib.request

BASE = Path(__file__).resolve().parents[1]


def check(upstream=False):
    supported = json.loads((BASE / 'shared/supportedLocales.json').read_text())
    catalogs = BASE / 'shared/rootfs/opt/nocturne-ha/locales'
    expected = json.loads((catalogs / 'en.json').read_text()).keys()
    if set(supported) != {p.stem for p in catalogs.glob('*.json')}:
        raise ValueError('Language coverage differs from Nocturne')
    for code in supported:
        translations = json.loads((catalogs / (code + '.json')).read_text(encoding='utf-8'))
        if translations.keys() != expected or any(not isinstance(t, str) or not t.strip() for t in translations.values()):
            raise ValueError('Incomplete catalog: ' + code)
    if upstream:
        request = urllib.request.Request('https://raw.githubusercontent.com/nightscout/nocturne/main/src/Web/supportedLocales.json', headers={'User-Agent': 'nocturne-ha-locales'})
        with urllib.request.urlopen(request, timeout=30) as response:
            current = json.load(response)
        if current != supported:
            raise ValueError('Nocturne language list changed; update and translate catalogs before promotion')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--upstream', action='store_true')
    check(parser.parse_args().upstream)
