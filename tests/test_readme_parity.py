"""README.md (es) and README.en.md (en) must document the same long options and the same bullet fields."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ES, EN = "README.md", "README.en.md"

# (file, element) -> reason. Elements that legitimately appear in only one README. Each needs a reason.
EXCEPTIONS: dict = {}

FENCE = re.compile(r"^(```|~~~).*?^\1[ \t]*$", re.S | re.M)
INLINE = re.compile(r"`([^`\n]+)`")
OPTION = re.compile(r"--[A-Za-z][A-Za-z0-9-]*")
FIELD = re.compile(r"^- `([^`\n]+)`:", re.M)


def _prose(text):
    """Text without fenced code blocks (only inline code counts)."""
    return FENCE.sub("", text)


def options(text):
    return {o for span in INLINE.findall(_prose(text)) for o in OPTION.findall(span)}


def fields(text):
    return set(FIELD.findall(_prose(text)))


def compare(es_text, en_text, es_name=ES, en_name=EN, exceptions=None):
    """Return a list of problems: what is documented in one file and missing from the other."""
    exceptions = EXCEPTIONS if exceptions is None else exceptions
    problems = []
    for kind, extract, fmt in (("option", options, "`{}`"), ("field", fields, "`{}`")):
        es, en = extract(es_text), extract(en_text)
        for item in sorted(es - en):
            if (en_name, item) not in exceptions and (es_name, item) not in exceptions:
                problems.append(f"{kind} {fmt.format(item)} is in {es_name} but missing from {en_name}")
        for item in sorted(en - es):
            if (es_name, item) not in exceptions and (en_name, item) not in exceptions:
                problems.append(f"{kind} {fmt.format(item)} is in {en_name} but missing from {es_name}")
    return problems


class ReadmeParityTest(unittest.TestCase):
    def test_readmes_document_the_same(self):
        es = (ROOT / ES).read_text(encoding="utf-8")
        en = (ROOT / EN).read_text(encoding="utf-8")
        problems = compare(es, en)
        self.assertEqual(problems, [], "\n" + "\n".join(problems))

    def test_finds_options_and_fields(self):
        text = (ROOT / EN).read_text(encoding="utf-8")
        self.assertGreater(len(options(text)), 3)
        self.assertIn("prompt", fields(text))

    def test_compare_names_missing_item_and_file(self):
        es = "- `key`: a\n- `prompt`: b\nUsa `gimg x --seed 3` y `--dry-run`.\n"
        en = "- `key`: a\nUse `--seed` only.\n"
        text = "\n".join(compare(es, en, "A.md", "B.md", exceptions={}))
        self.assertIn("field `prompt` is in A.md but missing from B.md", text)
        self.assertIn("option `--dry-run` is in A.md but missing from B.md", text)
        self.assertNotIn("`key`", text)
        self.assertNotIn("--seed", text)
        self.assertIn("field `extra` is in B.md but missing from A.md",
                      "\n".join(compare(es, en + "- `extra`: z\n", "A.md", "B.md", exceptions={})))

    def test_exceptions_and_fences_are_ignored(self):
        es = "```\n- `x`: y\n`--only-in-fence`\n```\n- `a`: 1\n"
        en = ""
        self.assertEqual(compare(es, en, "A.md", "B.md", exceptions={("B.md", "a"): "reason"}), [])


if __name__ == "__main__":
    unittest.main()
