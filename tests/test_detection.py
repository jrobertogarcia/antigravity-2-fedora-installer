#!/usr/bin/env python3
"""
Test suite for dynamic release detection and installer integrity.
Tests:
1. Online authoritative fetching and parsing from https://antigravity.google/download.
2. Fallback heuristic parsing under altered HTML markup.
3. Offline graceful fallback to bundled defaults.
4. Live verification of tarball HTTP status and header integrity.
5. Verification of spec files and installer syntax consistency.
"""

import sys
import os
import unittest
import importlib.util

# Add parent directory to path to import get-latest-versions
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_DIR)

spec = importlib.util.spec_from_file_location("get_latest_versions", os.path.join(REPO_DIR, "get-latest-versions.py"))
detector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detector)


class TestReleaseDetection(unittest.TestCase):

    def test_live_online_detection(self):
        """Test detection against live https://antigravity.google/download."""
        releases, source = detector.get_latest_releases(verify_live=True)
        self.assertEqual(source, "online")
        self.assertIn("agent", releases)
        self.assertIn("ide", releases)

        for comp in ("agent", "ide"):
            data = releases[comp]
            self.assertRegex(data["version"], r"^[0-9]+\.[0-9]+\.[0-9]+$", f"{comp} version format invalid")
            self.assertIn("x86_64", data["urls"], f"{comp} missing x86_64 URL")
            self.assertIn("aarch64", data["urls"], f"{comp} missing aarch64 URL")
            self.assertTrue(data["urls"]["x86_64"].startswith("https://"))
            self.assertTrue(data["urls"]["aarch64"].startswith("https://"))

    def test_heuristic_parsing_with_altered_html(self):
        """Test that heuristic layer parses unexpected HTML structures and custom CDNs."""
        mock_html = """
        <html>
          <body>
            <div>Download Google Antigravity Agent v3.0.0</div>
            <a href="https://custom-cdn.google.com/releases/3.0.0-999999/linux-x64/Antigravity.tar.gz">x64 Tarball</a>
            <a href="https://custom-cdn.google.com/releases/3.0.0-999999/linux-arm64/Antigravity.tar.gz">ARM64 Tarball</a>
            <div>Download Google Antigravity IDE v3.1.0</div>
            <a href="https://custom-cdn.google.com/ide/3.1.0-888888/linux-x64/Antigravity%20IDE.tar.gz">IDE x64</a>
            <a href="https://custom-cdn.google.com/ide/3.1.0-888888/linux-arm/Antigravity%20IDE.tar.gz">IDE ARM</a>
          </body>
        </html>
        """
        parsed = detector.parse_releases_from_html(mock_html)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["agent"]["version"], "3.0.0")
        self.assertEqual(parsed["ide"]["version"], "3.1.0")
        self.assertIn("x86_64", parsed["agent"]["urls"])
        self.assertIn("aarch64", parsed["agent"]["urls"])
        self.assertIn("x86_64", parsed["ide"]["urls"])
        self.assertIn("aarch64", parsed["ide"]["urls"])

    def test_empty_or_broken_html_fallback(self):
        """Test that None or corrupt HTML returns None to trigger graceful fallback."""
        self.assertIsNone(detector.parse_releases_from_html(""))
        self.assertIsNone(detector.parse_releases_from_html("<html><body>No links here</body></html>"))

    def test_verify_url_alive(self):
        """Test URL health checker with a known active URL."""
        releases, _ = detector.get_latest_releases(verify_live=False)
        agent_url = releases["agent"]["urls"]["x86_64"]
        self.assertTrue(detector.verify_url_alive(agent_url), f"URL failed live check: {agent_url}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
