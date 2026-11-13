import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class EnvIsolationTest(unittest.TestCase):
    def test_shell_gimg_vars_do_not_reach_the_tests(self):
        env = dict(os.environ, GIMG_CONFIG_HOME="/tmp/x-config", GIMG_DATA_HOME="/tmp/x-data",
                   GIMG_ENGINE="sdcpp", GIMG_AUTOSTART="1")
        code = ("import os, tests; "
                "print(sorted((n, v) for n, v in os.environ.items() if n.startswith('GIMG_')))")
        out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                             capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(out, "[('GIMG_AUTOSTART', '0')]")


if __name__ == "__main__":
    unittest.main()
