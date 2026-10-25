"""Errors that carry a stable code plus parameters, so any front end can render them."""
from __future__ import annotations

from . import i18n


class GimgError(Exception):
    """A user-facing error: `code` picks the text `error.<code>`, `params` fill it."""

    def __init__(self, code: str, errors=(), **params):
        super().__init__(code)
        self.code = code
        self.params = params
        self.errors = list(errors)  # schema ValidationError items, if any

    def message(self, lang: str | None = None) -> str:
        from . import schema

        text = i18n.t("error." + self.code, lang, **self.params)
        lines = [schema.format_error(e, lang) for e in self.errors]
        return "\n".join([text] + lines)

    def __str__(self):
        return "%s %r" % (self.code, self.params)


class PathError(GimgError):
    """A path from outside (project file, order) failed the D25 guard."""
