from __future__ import annotations

import json
import os
from pathlib import Path

_LOCALES = Path(__file__).parent / "locales"
_cache = {}
FALLBACK = "en"


def default_lang() -> str:
    explicit = os.environ.get("GIMG_LANG")
    if explicit:
        return explicit
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(var, "")
        if value.startswith("es"):
            return "es"
        if value:
            break
    return "en"


def _load(lang: str) -> dict:
    if lang not in _cache:
        path = _LOCALES / (lang + ".json")
        try:
            with open(path, encoding="utf-8") as fh:
                _cache[lang] = json.load(fh)
        except (OSError, ValueError):
            _cache[lang] = {}
    return _cache[lang]


def t(key: str, lang: str | None = None, **params) -> str:
    lang = lang or default_lang()
    for candidate in (lang, FALLBACK):
        text = _load(candidate).get(key)
        if text is not None:
            return text.format(**params)
    return key
