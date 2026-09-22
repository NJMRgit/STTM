"""The integrity rule the project's CI already enforces, as a test.

`install.sha256` must match the committed `install` script: a stale checksum
makes every clean curl-pipe download fail its own self check.
"""
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class InstallChecksum(unittest.TestCase):
    def test_install_matches_install_sha256(self):
        sums = ROOT / "install.sha256"
        self.assertTrue(sums.is_file(), "install.sha256 is missing")
        fields = sums.read_text().split()
        self.assertGreaterEqual(len(fields), 2, "install.sha256 is not sha256sum output")
        expected, name = fields[0], fields[1].lstrip("*")
        script = ROOT / name
        self.assertTrue(script.is_file(), f"install.sha256 names a missing file: {name}")
        actual = hashlib.sha256(script.read_bytes()).hexdigest()
        self.assertEqual(
            actual,
            expected,
            "install.sha256 is out of sync with install; run: sha256sum install > install.sha256",
        )


if __name__ == "__main__":
    unittest.main()
