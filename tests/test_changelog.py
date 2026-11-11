"""Si la rama toca `gimg/`, «[Sin publicar]» / «[Unreleased]» de los CHANGELOG tiene alguna entrada (REVIEW.md).

La lógica es pura (`unreleased_problem`, texto + rutas -> motivo o None) y se prueba con textos de ejemplo; la prueba
del repo solo añade la llamada a git. Casos límite: sin git o sin `origin/main` y clon superficial sin merge-base se
saltan con motivo; HEAD en `origin/main` o un diff sin `gimg/` pasan; una release recién numerada (`releases.py bump`
mueve las entradas a la versión nueva y deja vacío lo sin publicar) pasa si esa versión aún no está en `origin/main`.
`origin/main` está en el CI: `check.yml` hace checkout con `fetch-depth: 0`."""
import re
import subprocess
import unittest
from pathlib import Path

import releases

ROOT = Path(__file__).resolve().parent.parent
FILES = {"es": "CHANGELOG.es.md", "en": "CHANGELOG.md"}
_HEADING = re.compile(r"^## \[([^\]]+)\]")


def has_entries(text, version):
    """Hay alguna línea `- …` en la sección `## [version]`, antes del siguiente `## [`."""
    inside = False
    for line in text.splitlines():
        found = _HEADING.match(line)
        if found:
            if inside:
                return False
            inside = found.group(1) == version
        elif inside and line.startswith("- "):
            return True
    return False


def unreleased_problem(text, base_text, paths):
    """El motivo por el que el CHANGELOG `text` no vale para los cambios `paths`, o None.

    `base_text` es el CHANGELOG de `origin/main` (None si no se tiene)."""
    if not any(p.startswith("gimg/") for p in paths):
        return None
    unreleased = next((m.group(1) for m in map(_HEADING.match, text.splitlines()) if m
                       and releases._UNRELEASED.match(m.group(0))), None)
    if unreleased is None:
        return "no tiene la sección «[Sin publicar]» / «[Unreleased]»"
    if has_entries(text, unreleased):
        return None
    newest = next((m.group(1) for m in map(_HEADING.match, text.splitlines()) if m and m.group(1) != unreleased), None)
    if newest and base_text is not None and releases.section(base_text, newest) is None:
        return None  # release recién numerada: sus entradas están en la versión nueva
    return "la sección «[%s]» no tiene ninguna entrada (`- …`) y la rama toca gimg/" % unreleased


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


class PureLogic(unittest.TestCase):
    FULL = "# C\n\n## [Unreleased]\n\n### Added\n\n- Algo.\n\n## [0.4.0] - 2026-11-05\n\n- Viejo.\n"
    EMPTY = "# C\n\n## [Unreleased]\n\n## [0.4.0] - 2026-11-05\n\n- Viejo.\n"
    BUMPED = "# C\n\n## [Unreleased]\n\n## [0.5.0] - 2026-11-12\n\n- Nuevo.\n\n## [0.4.0] - 2026-11-05\n\n- Viejo.\n"
    GIMG = ["gimg/ui/app.js"]

    def test_entry_passes(self):
        self.assertIsNone(unreleased_problem(self.FULL, self.FULL, self.GIMG))

    def test_empty_section_fails_with_its_reason(self):
        problem = unreleased_problem(self.EMPTY, self.EMPTY, self.GIMG)
        self.assertIn("no tiene ninguna entrada", problem)
        self.assertIn("[Unreleased]", problem)

    def test_entries_of_the_next_version_do_not_count(self):
        self.assertIn("ninguna entrada", unreleased_problem(self.EMPTY, self.FULL, self.GIMG))

    def test_without_gimg_changes_passes(self):
        self.assertIsNone(unreleased_problem(self.EMPTY, self.EMPTY, ["docs/x.md", "tests/test_x.py"]))
        self.assertIsNone(unreleased_problem(self.EMPTY, self.EMPTY, []))

    def test_fresh_release_passes_only_if_version_is_new_in_base(self):
        self.assertIsNone(unreleased_problem(self.BUMPED, self.EMPTY, self.GIMG))
        self.assertIn("ninguna entrada", unreleased_problem(self.BUMPED, self.BUMPED, self.GIMG))

    def test_missing_section_fails(self):
        self.assertIn("no tiene la sección", unreleased_problem("# C\n\n## [0.4.0]\n\n- x\n", None, self.GIMG))

    def test_spanish_heading(self):
        self.assertIn("[Sin publicar]", unreleased_problem(self.EMPTY.replace("Unreleased", "Sin publicar"), None, self.GIMG))


class RepoChangelogs(unittest.TestCase):
    def test_branch_touching_gimg_has_unreleased_entries(self):
        try:
            if git("rev-parse", "--git-dir").returncode != 0:
                self.skipTest("no hay git")
            if git("rev-parse", "--verify", "--quiet", "origin/main").returncode != 0:
                self.skipTest("no hay origin/main (git fetch origin main)")
            base = git("merge-base", "origin/main", "HEAD")
        except OSError:
            self.skipTest("no hay git")
        if base.returncode != 0 or not base.stdout.strip():
            self.skipTest("clon superficial: sin merge-base con origin/main")
        paths = git("diff", "--name-only", base.stdout.strip(), "HEAD", "--", "gimg/").stdout.split()
        for name in FILES.values():
            shown = git("show", "origin/main:" + name)
            problem = unreleased_problem((ROOT / name).read_text(encoding="utf-8"),
                                         shown.stdout if shown.returncode == 0 else None, paths)
            self.assertIsNone(problem, "%s: %s" % (name, problem))


if __name__ == "__main__":
    unittest.main()
