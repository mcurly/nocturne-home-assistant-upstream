"""HA-compatible package numbering; upstream versions remain separate metadata."""
import argparse
import re
from awesomeversion import AwesomeVersion

PLAIN = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')


def require_upgrade(candidate, previous=None):
    if not PLAIN.fullmatch(candidate):
        raise ValueError('Package version must be plain MAJOR.MINOR.PATCH without suffixes')
    if previous and not AwesomeVersion(candidate) > AwesomeVersion(previous):
        raise ValueError(f'Package {candidate} is not newer than {previous} according to Home Assistant')


def next_version(previous, run_number, attempt):
    if run_number < 1 or not 1 <= attempt < 100:
        raise ValueError('Invalid publication run/attempt counter')
    # The existing store remains authoritative even if the workflow counter resets.
    bases = [(0, 2, 0)]
    for version in previous:
        match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:-\d+)?', version)
        if not match:
            raise ValueError('Unrecognized previous package version: ' + version)
        bases.append(tuple(map(int, match.groups())))
    major, minor, patch = max(bases)
    result = f'{major}.{minor}.{max(patch + 1, run_number * 100 + attempt)}'
    for version in previous:
        require_upgrade(result, version)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repository', required=True)
    parser.add_argument('--run-number', type=int, required=True)
    parser.add_argument('--attempt', type=int, required=True)
    args = parser.parse_args()
    from candidate import previous_package
    previous = [p['version'] for channel in ('stable', 'main')
                if (p := previous_package(args.repository, channel))]
    print(next_version(previous, args.run_number, args.attempt))
