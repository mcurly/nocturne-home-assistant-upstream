import sys
from pathlib import Path
import unittest
from awesomeversion import AwesomeVersion

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from versions import next_version, require_upgrade


class VersionTests(unittest.TestCase):
    def test_recovers_both_legacy_installations(self):
        version = next_version(['0.2.0-201', '0.2.0-401'], 5, 1)
        self.assertEqual(version, '0.2.501')
        for previous in ['0.2.0-201', '0.2.0-401']:
            self.assertTrue(AwesomeVersion(version) > previous)

    def test_does_not_reintroduce_broken_suffix_comparison(self):
        self.assertFalse(AwesomeVersion('0.2.0-401') > '0.2.0-201')
        for version in ['0.2.0-501', '0.2.0+501', '0.2.0beta1', '0.02.1']:
            with self.assertRaises(ValueError):
                require_upgrade(version)

    def test_rejects_equal_or_older_publication(self):
        for version in ['0.2.501', '0.2.500', '0.1.999']:
            with self.assertRaises(ValueError):
                require_upgrade(version, '0.2.501')

    def test_retry_reset_and_different_channel_versions(self):
        self.assertEqual(next_version(['0.2.501'], 5, 2), '0.2.502')
        self.assertEqual(next_version(['0.2.900', '0.2.501'], 1, 1), '0.2.901')
        self.assertEqual(next_version(['0.3.10'], 1, 1), '0.3.101')

    def test_invalid_counter_or_previous_version_stops_publication(self):
        for run, attempt in [(0, 1), (1, 0), (1, 100)]:
            with self.assertRaises(ValueError):
                next_version([], run, attempt)
        with self.assertRaises(ValueError):
            next_version(['unrecognized'], 1, 1)
