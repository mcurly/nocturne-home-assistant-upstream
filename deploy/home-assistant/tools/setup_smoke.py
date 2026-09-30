"""Real container failure rehearsal; never touches an existing installation."""
import argparse
import json
import time
import uuid
from smoke import docker, execute


def main(image):
    name = 'nocturne-setup-ci-' + uuid.uuid4().hex
    volume = name + '-data'
    docker('volume', 'create', volume)
    try:
        options = {'public_url': 'https://nocturne.example.net:8448',
                   'certificate': 'missing-chain.pem', 'private_key': 'missing-key.pem'}
        docker('run', '--rm', '-i', '--entrypoint', 'python3', '-v', volume + ':/data', image, '-', input=
               "from pathlib import Path\nPath('/data/options.json').write_text(" + repr(json.dumps(options)) + ')\n')
        docker('run', '-d', '--name', name, '-v', volume + ':/data', image)
        code = '''
import urllib.request, urllib.error
from pathlib import Path
assert not (Path('/data/postgres') / 'PG_VERSION').exists()
try:
    urllib.request.urlopen('http://127.0.0.1:8099/', timeout=3)
except urllib.error.HTTPError as error:
    assert error.code == 403
else:
    raise AssertionError('Ingress accepted a direct client')
'''
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                execute(name, code)
                break
            except RuntimeError:
                time.sleep(1)
        else:
            raise RuntimeError('Help listener unavailable with missing certificate')
        time.sleep(3)
        assert docker('inspect', '--format', '{{.State.Running}}', name) == 'true'
        execute(name, code)
        print('PASS: missing certificate preserves the ingress listener; no database initialized')
    finally:
        docker('rm', '-f', name, check=False)
        docker('volume', 'rm', volume, check=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True)
    main(parser.parse_args().image)
