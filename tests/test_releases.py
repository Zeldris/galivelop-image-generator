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
            base = "https://github.com/Zeldris/galivelop-image-generator/blob/v0.3.0"
            self.assertEqual(text, "**ES** · [English below](#en)\n\n"
                                   "## Español\n\n#### Añadido\n\n- Thing three.\n\n"
                                   '<a id="en"></a>\n\n'
                                   "## English\n\n#### Added\n\n- Thing three.\n\n"
                                   f"Full entry / Entrada completa: [CHANGELOG.md]({base}/CHANGELOG.md) · "
                                   f"[CHANGELOG.es.md]({base}/CHANGELOG.es.md)\n")
            with self.assertRaisesRegex(ValueError, r"CHANGELOG\.es\.md no tiene la sección ## \[0\.2\.0\]"):
                releases.notes("0.2.0", root)

    def test_the_current_version_has_notes_in_both_changelogs(self):
        version = releases._VERSION.search((R / "gimg" / "__init__.py").read_text(encoding="utf-8")).group(1)
        text = releases.notes(version)
        self.assertIn("## Español", text)
        self.assertIn("## English", text)

    def test_both_changelogs_have_the_same_versions_and_items(self):
        def items(name):
            out, current = {}, None
            for line in (R / name).read_text(encoding="utf-8").splitlines():
                if line.startswith("## ["):
                    current = line[4:line.index("]")].replace("Sin publicar", "Unreleased")
                    out[current] = 0
                elif current and line.startswith("- "):
                    out[current] += 1
            return out
        self.assertEqual(items("CHANGELOG.es.md"), items("CHANGELOG.md"),
                         "versiones y número de puntos (por versión) de CHANGELOG.es.md frente a CHANGELOG.md")


def project(tmp, version="0.4.0", en="- New thing.\n", es="- Cosa nueva.\n"):
    root = Path(tmp)
    (root / "gimg").mkdir()
    (root / "gimg" / "__init__.py").write_text(f'__version__ = "{version}"\n', encoding="utf-8")
    (root / "CHANGELOG.md").write_text(f"# Changelog\n\n## [Unreleased]\n\n{en}\n## [0.4.0] - 2026-11-05\n\n- Old.\n",
                                       encoding="utf-8")
    (root / "CHANGELOG.es.md").write_text(
        f"# Registro\n\n## [Sin publicar]\n\n{es}\n## [0.4.0] - 2026-11-05\n\n- Viejo.\n", encoding="utf-8")
    return root


class BumpTests(unittest.TestCase):
    def test_bump_moves_unreleased_into_a_new_section_and_sets_the_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            releases.bump("0.5.0", "2026-12-01", root)
            self.assertEqual((root / "gimg" / "__init__.py").read_text(), '__version__ = "0.5.0"\n')
            self.assertEqual((root / "CHANGELOG.md").read_text(),
                             "# Changelog\n\n## [Unreleased]\n\n## [0.5.0] - 2026-12-01\n\n- New thing.\n\n"
                             "## [0.4.0] - 2026-11-05\n\n- Old.\n")
            self.assertEqual((root / "CHANGELOG.es.md").read_text(),
                             "# Registro\n\n## [Sin publicar]\n\n## [0.5.0] - 2026-12-01\n\n- Cosa nueva.\n\n"
                             "## [0.4.0] - 2026-11-05\n\n- Viejo.\n")
            self.assertEqual(releases.notes("0.5.0", root).count("New thing"), 1)

    def test_bump_defaults_to_today(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp)
            releases.bump("0.4.1", root=root)
            today = releases.datetime.date.today().isoformat()
            self.assertIn(f"## [0.4.1] - {today}", (root / "CHANGELOG.md").read_text())

    def refuses(self, reason, version="0.5.0", **kw):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp, **kw)
            before = {p.name: p.read_text() for p in root.rglob("*") if p.is_file()}
            with self.assertRaisesRegex(ValueError, reason):
                releases.bump(version, root=root)
            self.assertEqual(before, {p.name: p.read_text() for p in root.rglob("*") if p.is_file()})

    def test_bump_refuses_a_version_that_is_not_greater(self):
        self.refuses("no es mayor que la versión actual 0.4.0", "0.4.0")
        self.refuses("no es mayor que la versión actual 0.4.0", "0.3.9")

    def test_bump_refuses_non_semver(self):
        self.refuses("no es una versión semver", "0.5")
        self.refuses("no es una versión semver", "v0.5.0")

    def test_bump_refuses_an_empty_unreleased_in_any_changelog_and_writes_nothing(self):
        self.refuses(r"CHANGELOG\.es\.md no tiene nada sin publicar", es="")
        self.refuses(r"CHANGELOG\.md no tiene nada sin publicar", en="")

    def test_bump_cli_exit_codes(self):
        self.assertEqual(releases.main(["bump", "0.5"]), 1)
        self.assertEqual(releases.main(["bump", "0.5.0", "--fecha", "x"]), 2)


def log_run(tag, commits):
    def run(argv, **_):
        if argv[:2] == ["git", "describe"]:
            if tag is None:
                raise subprocess.CalledProcessError(128, argv)
            return subprocess.CompletedProcess(argv, 0, tag + "\n", "")
        assert argv[:2] == ["git", "log"] and argv[-1] == f"{tag}..HEAD", argv
        return subprocess.CompletedProcess(argv, 0, "".join(c + "\x00\n" for c in commits), "")
    return run


class SuggestTests(unittest.TestCase):
    def test_feat_is_minor_fix_is_patch(self):
        code, msg = releases.suggest(log_run("v0.4.0", ["fix(F4): a\n", "feat(F4): b\n\ncuerpo"]))
        self.assertEqual(code, 0)
        self.assertTrue(msg.startswith("0.5.0 (minor, desde v0.4.0)"), msg)
        self.assertIn("feat(F4): b", msg)
        code, msg = releases.suggest(log_run("v0.4.0", ["perf: a\n", "docs: x\n"]))
        self.assertTrue(msg.startswith("0.4.1 (patch"), msg)

    def test_breaking_is_minor_in_0x_and_major_from_1(self):
        for commits in (["fix!: a\n"], ["fix: a\n\nBREAKING CHANGE: x"]):
            self.assertTrue(releases.suggest(log_run("v0.4.0", commits))[1].startswith("0.5.0 (minor"))
            self.assertTrue(releases.suggest(log_run("v1.2.3", commits))[1].startswith("2.0.0 (major"))

    def test_nothing_suggests_none(self):
        code, msg = releases.suggest(log_run("v0.4.0", ["docs: a\n", "chore: b\n"]))
        self.assertEqual(code, 0)
        self.assertTrue(msg.startswith("ninguna: ningún commit desde v0.4.0"), msg)

    def test_no_tag_is_unknown(self):
        code, msg = releases.suggest(log_run(None, []))
        self.assertEqual((code, "no se puede leer el historial" in msg), (2, True))


class VerifyTagTests(unittest.TestCase):
    def test_matching_tag(self):
        self.assertEqual(releases.verify_tag("v0.4.0", "abc", fake_run())[0], 0)

    def test_mismatch_says_both_versions(self):
        code, msg = releases.verify_tag("v0.5.0", "abc", fake_run())
        self.assertEqual(code, 1)
        self.assertIn("v0.5.0 no coincide con __version__ = 0.4.0", msg)

    def test_malformed_tag(self):
        code, msg = releases.verify_tag("0.4.0", "abc", fake_run())
        self.assertEqual((code, "no tiene la forma vX.Y.Z" in msg), (1, True))


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


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_installs_what_the_check_needs_like_check_yml(self):
        # Sin `ciInstall` (ffmpeg, rsvg-convert) el check de release.yml falla y no crea la release (v0.4.0).
        wf = (R / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        install, check = wf.find("config.py get ciInstall)"), wf.find("config.py get check)")
        self.assertNotEqual(install, -1, "release.yml no instala `ciInstall` de .claude/gw.json")
        self.assertNotEqual(check, -1, "release.yml no corre `check` de .claude/gw.json")
        self.assertLess(install, check, "release.yml instala después de correr el check")

    def test_release_runs_install_and_check_like_check_yml(self):
        # release.yml copia pasos de check.yml (retro 2026-11-05, P1): si se desvían, el check de la release no es el
        # del PR (v0.4.0 falló sin `ciInstall`; la fase 1 vio Python 3.10 frente al del runner).
        check, release = _workflow_steps("check.yml"), _workflow_steps("release.yml")
        for name in ("Install", "Check"):
            self.assertIsNotNone(check.get(name), f"check.yml no tiene el paso «{name}»: actualiza este test")
            self.assertEqual(release.get(name), check.get(name), f"«{name}» de release.yml no es el de check.yml")
        setup = check.get("actions/setup-python@v5", [])
        if any(line.startswith("if: hashFiles(") for line in setup):
            self.assertFalse("actions/setup-python@v5" in release, "release.yml fija Python; check.yml, el del runner")


def _workflow_steps(name):
    """Pasos de un workflow por `name:` (o `uses:`), con sus líneas sin comentarios ni `</dev/null` final."""
    steps, current = {}, None
    for raw in (R / ".github" / "workflows" / name).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if raw.startswith("      - "):
            line = line[2:]
            key = line.split(": ", 1)[1].strip() if line.startswith(("name:", "uses:")) else None
            current = None if key is None else steps.setdefault(key, [])
            continue
        if current is None or not line or line.startswith("#") or not raw.startswith("        "):
            continue
        current.append(line.removesuffix(" </dev/null"))
    return steps


if __name__ == "__main__":
    unittest.main()
