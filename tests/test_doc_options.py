"""Every `gimg ...` fragment in the changelogs and READMEs must match the real argparse parser."""
import argparse
import re
import unittest
from pathlib import Path

from gimg import cli

ROOT = Path(__file__).resolve().parent.parent
DOC_FILES = ["CHANGELOG.md", "CHANGELOG.es.md", "README.md", "README.en.md"]

# (file, fragment) pairs that are legitimate but do not match the parser. Each needs a reason.
EXCEPTIONS: dict = {}

FRAGMENT = re.compile(r"`(gimg [^`\n]*)`")
OPTION = re.compile(r"--[A-Za-z][A-Za-z0-9-]*")


def _subparsers(parser):
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action.choices
    return None


def _options(parser):
    return {s for a in parser._actions for s in a.option_strings}


def check_fragment(parser, fragment):
    """Return a list of problems (empty when the fragment matches the parser)."""
    tokens = fragment.split()[1:]
    root_opts = _options(parser)
    nodes = [parser]  # all parsers reached so far (alternatives a|b|c fan out)
    problems = []
    for token in tokens:
        if token.startswith("-"):
            for opt in OPTION.findall(token):
                bad = [n for n in nodes if opt not in _options(n) and opt not in root_opts]
                if bad:
                    problems.append(f"option {opt} does not exist in the command ({', '.join(sorted(_names(bad, parser)))})")
            continue
        if not re.fullmatch(r"[a-z][a-z0-9_-]*(\|[a-z][a-z0-9_-]*)*", token):
            continue  # placeholder, value or prose: not a command
        subs = [(n, _subparsers(n)) for n in nodes]
        if not any(c for _n, c in subs):
            continue  # leaf: positional value
        nxt = []
        for node, choices in subs:
            if not choices:
                nxt.append(node)
                continue
            for alt in token.split("|"):
                if alt in choices:
                    nxt.append(choices[alt])
                else:
                    problems.append(f"command '{alt}' does not exist (valid: {', '.join(choices)})")
        nodes = nxt or nodes
    return problems


def _names(nodes, root):
    return [n.prog for n in nodes]


class DocOptionsTest(unittest.TestCase):
    def _fragments(self, files):
        for name in files:
            text = (ROOT / name).read_text(encoding="utf-8") if not isinstance(name, Path) else name.read_text(encoding="utf-8")
            for m in FRAGMENT.finditer(text):
                yield str(name), m.group(1).strip()

    def _failures(self, files):
        parser = cli._build("en")
        out = []
        for name, frag in self._fragments(files):
            if (name, frag) in EXCEPTIONS:
                continue
            for problem in check_fragment(parser, frag):
                out.append(f"{name}: `{frag}`: {problem}")
        return out

    def test_docs_match_parser(self):
        failures = self._failures(DOC_FILES)
        self.assertEqual(failures, [], "\n" + "\n".join(failures))

    def test_finds_fragments(self):
        self.assertGreater(len(list(self._fragments(DOC_FILES))), 10)

    def test_detects_unknown_option_and_command(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.md"
            f.write_text("`gimg doctor --project` `gimg queue list|nope` `gimg doctor --verify` `gimg order submit|list`\n",
                         encoding="utf-8")
            failures = self._failures([f])
        text = "\n".join(failures)
        self.assertIn("`gimg doctor --project`: option --project does not exist", text)
        self.assertIn("`gimg queue list|nope`: command 'nope' does not exist", text)
        self.assertNotIn("--verify", text)
        self.assertNotIn("order submit|list`:", text)


if __name__ == "__main__":
    unittest.main()
