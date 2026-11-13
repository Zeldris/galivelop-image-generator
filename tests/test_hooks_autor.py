"""Con agentSignatures: false, commit-msg y pre-push rechazan los commits a nombre del agente (noreply@anthropic.com)."""
import os
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT = {"GIT_AUTHOR_NAME": "Claude", "GIT_AUTHOR_EMAIL": "noreply@anthropic.com",
         "GIT_COMMITTER_NAME": "Claude", "GIT_COMMITTER_EMAIL": "noreply@anthropic.com"}
PERSON = {"GIT_AUTHOR_NAME": "Persona", "GIT_AUTHOR_EMAIL": "persona@example.com",
          "GIT_COMMITTER_NAME": "Persona", "GIT_COMMITTER_EMAIL": "persona@example.com"}
MESSAGE = "test(autor): mensaje de prueba\n\nCuerpo.\n\nSiguiente: nada.\n"


def _env(ident):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(ident)
    return env


class CommitMsgAuthorTest(unittest.TestCase):
    def _run(self, ident):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
            fh.write(MESSAGE)
        self.addCleanup(os.unlink, fh.name)
        return subprocess.run(["bash", os.path.join(ROOT, ".githooks", "commit-msg"), fh.name], cwd=ROOT,
                              env=_env(ident), capture_output=True, text=True, timeout=120)

    def test_rechaza_el_autor_agente(self):
        res = self._run(AGENT)
        self.assertEqual(res.returncode, 1, res.stderr)
        self.assertIn("author is the agent", res.stderr)

    def test_rechaza_solo_el_committer_agente(self):
        ident = dict(PERSON, GIT_COMMITTER_NAME="Claude", GIT_COMMITTER_EMAIL="NoReply@Anthropic.com")
        res = self._run(ident)
        self.assertEqual(res.returncode, 1, res.stderr)
        self.assertIn("committer is the agent", res.stderr)

    def test_deja_pasar_a_la_persona(self):
        res = self._run(PERSON)
        self.assertNotIn("is the agent", res.stderr)
        self.assertEqual(res.returncode, 0, res.stderr)


class PrePushAuthorTest(unittest.TestCase):
    def test_rechaza_un_commit_del_agente(self):
        env = _env(AGENT)
        sha = subprocess.run(["git", "commit-tree", "HEAD^{tree}", "-p", "HEAD", "-m", "prueba"], cwd=ROOT, env=env,
                             capture_output=True, text=True, check=True).stdout.strip()
        line = "refs/heads/prueba-autor %s refs/heads/prueba-autor %s\n" % (sha, "0" * 40)
        res = subprocess.run(["bash", os.path.join(ROOT, ".githooks", "pre-push"), "origin", "file:///nada"],
                             cwd=ROOT, env=_env({}), input=line, capture_output=True, text=True, timeout=300)
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertIn("authored or committed as the agent", res.stderr)
        self.assertIn(sha[:7], res.stderr)


if __name__ == "__main__":
    unittest.main()
