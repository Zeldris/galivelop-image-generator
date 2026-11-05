"""releases.py: notas de la release desde los CHANGELOG y comprobación de etiqueta y release (sin red: run falso)."""
import subprocess
import tempfile
import unittest
from pathlib import Path

import releases

R = Path(__file__).resolve().parents[1]

CHANGELOG = """# Changelog

## [Unreleased]

## [0.4.0] - 2026-11-05

### Added

- Thing four.

## [0.3.0] - 2026-11-05

### Added

- Thing three.
"""


def fake_run(version='"0.4.0"', tag=True, release="ok", calls=None):
    calls = [] if calls is None else calls

    def run(argv, **_):
        if argv[:2] == ["git", "show"]:
            return subprocess.CompletedProcess(argv, 0, f"__version__ = {version}\n", "")
        if argv[:2] == ["git", "fetch"]:
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv[:2] == ["git", "ls-remote"]:
            return subprocess.CompletedProcess(argv, 0, "abc\trefs/tags/v0.4.0\n" if tag else "", "")
        if release == "ok":
            return subprocess.CompletedProcess(argv, 0, '{"tagName":"v0.4.0"}', "")
        return subprocess.CompletedProcess(argv, 1, "", release)
    return run


class NotesTests(unittest.TestCase):
    def test_section_takes_only_its_version(self):
        self.assertEqual(releases.section(CHANGELOG, "0.4.0"), "### Added\n\n- Thing four.")
        self.assertIsNone(releases.section(CHANGELOG, "0.2.0"))

    def test_notes_join_both_changelogs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
            (root / "CHANGELOG.es.md").write_text(CHANGELOG.replace("Added", "Añadido"), encoding="utf-8")
            text = releases.notes("0.3.0", root)
            self.assertEqual(text, "## Español\n\n#### Añadido\n\n- Thing three.\n\n"
                                   "## English\n\n#### Added\n\n- Thing three.\n")
            with self.assertRaisesRegex(ValueError, r"CHANGELOG\.es\.md no tiene la sección ## \[0\.2\.0\]"):
                releases.notes("0.2.0", root)

    def test_the_current_version_has_notes_in_both_changelogs(self):
        version = releases._VERSION.search((R / "gimg" / "__init__.py").read_text(encoding="utf-8")).group(1)
        text = releases.notes(version)
        self.assertIn("## Español", text)
        self.assertIn("## English", text)


class CheckTests(unittest.TestCase):
    def test_all_there(self):
        self.assertEqual(releases.check("origin/main", fake_run()),
                         (0, "releases: gimg 0.4.0 (origin/main) tiene etiqueta y release"))

    def test_missing_tag_and_release_say_how_to_make_them(self):
        code, message = releases.check("origin/main", fake_run(tag=False, release="release not found"))
        self.assertEqual(code, 1)
        self.assertIn("git tag -a v0.4.0", message)
        self.assertIn("gh release create v0.4.0", message)
        self.assertNotIn("notas.md", message)

    def test_fetches_the_remote_branch_before_reading_the_version(self):
        calls = []
        releases.check("origin/main", fake_run(calls=calls))
        self.assertEqual(calls, [["git", "fetch", "--quiet", "origin", "main"]])
        calls.clear()
        releases.check("v0.3.0", fake_run(calls=calls))
        self.assertEqual(calls, [])

    def test_repo_not_found_is_unknown_not_missing(self):
        code, message = releases.check("origin/main", fake_run(release="HTTP 404: Not Found"))
        self.assertEqual((code, "gh no responde (HTTP 404: Not Found)" in message), (2, True))

    def test_check_rejects_an_option_as_ref(self):
        self.assertEqual(releases.main(["check", "--ref", "--ref"]), 2)

    def test_gh_failing_for_another_reason_is_unknown_not_missing(self):
        code, message = releases.check("origin/main", fake_run(release="HTTP 503"))
        self.assertEqual((code, "gh no responde (HTTP 503)" in message), (2, True))

    def test_no_version_is_unknown(self):
        code, message = releases.check("origin/main", fake_run(version="None"))
        self.assertEqual((code, "no tiene __version__" in message), (2, True))


if __name__ == "__main__":
    unittest.main()
