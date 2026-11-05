"""F4e: which browser the real-browser tests use (tests/browser.py ``find_browser``), with nothing taken from the machine."""
import os
import unittest
from unittest import mock

from tests import browser

FF = ["/usr/bin/firefox"]
CH = ["/usr/bin/google-chrome"]


def choose(env=None, desktop=None, firefox=FF, chrome=CH):
    with mock.patch.dict(os.environ, env or {}, clear=True), \
            mock.patch.object(browser, "default_desktop", return_value=desktop), \
            mock.patch.object(browser, "find_firefox", return_value=firefox), \
            mock.patch.object(browser, "find_chrome", return_value=chrome):
        return browser.find_browser()


class KindOf(unittest.TestCase):
    def test_desktop_files_and_commands(self):
        self.assertEqual(browser.kind_of("org.mozilla.firefox.desktop"), "firefox")
        self.assertEqual(browser.kind_of("firefox-esr.desktop"), "firefox")
        self.assertEqual(browser.kind_of("google-chrome.desktop"), "chrome")
        self.assertEqual(browser.kind_of("org.chromium.Chromium.desktop"), "chrome")
        self.assertEqual(browser.kind_of("flatpak run com.google.Chrome"), "chrome")
        self.assertIsNone(browser.kind_of("org.gnome.Epiphany.desktop"))


class FindBrowser(unittest.TestCase):
    def test_default_browser_wins(self):
        self.assertEqual(choose(desktop="org.mozilla.firefox.desktop"), ("firefox", FF))
        self.assertEqual(choose(desktop="google-chrome.desktop"), ("chrome", CH))

    def test_unknown_default_falls_back_to_firefox_then_chrome(self):
        self.assertEqual(choose(desktop="org.gnome.Epiphany.desktop"), ("firefox", FF))
        self.assertEqual(choose(desktop=None, firefox=None), ("chrome", CH))

    def test_default_not_installed_falls_back_to_the_other(self):
        self.assertEqual(choose(desktop="org.mozilla.firefox.desktop", firefox=None), ("chrome", CH))

    def test_none_found(self):
        self.assertIsNone(choose(firefox=None, chrome=None))

    def test_env_command_overrides_everything(self):
        self.assertEqual(choose({"GIMG_TEST_BROWSER": "flatpak run org.mozilla.firefox"}, "google-chrome.desktop"),
                         ("firefox", ["flatpak", "run", "org.mozilla.firefox"]))
        self.assertEqual(choose({"GIMG_TEST_BROWSER": "/opt/br/other --x"}, "org.mozilla.firefox.desktop"),
                         ("chrome", ["/opt/br/other", "--x"]))

    def test_legacy_chrome_variable_forces_chrome(self):
        self.assertEqual(choose({"GIMG_TEST_CHROME": "my chrome"}, "org.mozilla.firefox.desktop"),
                         ("chrome", ["my", "chrome"]))


class FlatpakArgs(unittest.TestCase):
    def test_options_go_right_after_run(self):
        cmd = ["flatpak-spawn", "--host", "flatpak", "run", "org.mozilla.firefox"]
        self.assertEqual(browser._flatpak_args(cmd, "--filesystem=/x"),
                         ["flatpak-spawn", "--host", "flatpak", "run", "--filesystem=/x", "org.mozilla.firefox"])
        self.assertEqual(browser._flatpak_args(["/usr/bin/firefox"], "--filesystem=/x"), ["/usr/bin/firefox"])


if __name__ == "__main__":
    unittest.main()
