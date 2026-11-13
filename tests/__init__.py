import os

# The tests never see the GIMG_* of the shell that runs them (a `git push` with GIMG_CONFIG_HOME/GIMG_DATA_HOME
# exported failed the pre-push, 2026-11-11): each test sets the ones it needs.
# GIMG_TEST_* are the harness's own settings (tests/browser.py) and stay.
for _name in [n for n in os.environ if n.startswith("GIMG_") and not n.startswith("GIMG_TEST_")]:
    del os.environ[_name]

# No test starts the local service by accident (F3.5); the ones that want it set GIMG_AUTOSTART=1 themselves.
os.environ["GIMG_AUTOSTART"] = "0"
