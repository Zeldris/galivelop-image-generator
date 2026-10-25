"""Small strict validator for the JSON Schema subset used by gimg."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import NamedTuple

from . import i18n

_SCHEMAS = Path(__file__).parent / "schemas"

ANNOTATIONS = frozenset(
    ["$schema", "$id", "title", "description", "default", "examples", "$comment"]
)
VALIDATING = frozenset(
    [
        "type", "properties", "required", "additionalProperties", "propertyNames",
        "minProperties", "items", "minItems", "maxItems", "enum", "const", "pattern",
        "minLength", "maxLength", "minimum", "maximum", "$ref", "$defs",
    ]
)
# Every code format_error may be asked to render.
CODES = (
    "required", "type", "enum", "const", "pattern", "minimum", "maximum",
    "minLength", "maxLength", "minItems", "maxItems", "minProperties",
    "additionalProperties", "propertyNames",
)
TYPES = ("object", "array", "string", "integer", "number", "boolean", "null")


class SchemaError(Exception):
    pass


class ValidationError(NamedTuple):
    path: str
    code: str
    params: dict


def _check_schema(schema, where="#"):
    if isinstance(schema, bool):
        return
    if not isinstance(schema, dict):
        raise SchemaError("%s: schema must be an object" % where)
    for key, value in schema.items():
        if key in ANNOTATIONS:
            continue
        if key not in VALIDATING:
            raise SchemaError("%s: unsupported keyword %r" % (where, key))
        if key in ("properties", "$defs"):
            for name, sub in value.items():
                _check_schema(sub, "%s/%s/%s" % (where, key, name))
        elif key in ("items", "propertyNames") or (
            key == "additionalProperties" and not isinstance(value, bool)
        ):
            _check_schema(value, "%s/%s" % (where, key))
        elif key == "type":
            names = value if isinstance(value, list) else [value]
            for name in names:
                if name not in TYPES:
                    raise SchemaError("%s: unknown type %r" % (where, name))
        elif key == "$ref" and not (isinstance(value, str) and value.startswith("#/")):
            raise SchemaError("%s: only local '#/...' references are supported" % where)


def check_schema(schema: dict) -> None:
    _check_schema(schema)


def load_schema(name: str) -> dict:
    path = _SCHEMAS / (name + ".schema.json")
    with open(path, encoding="utf-8") as fh:
        schema = json.load(fh)
    check_schema(schema)
    return schema


def _is_type(value, name):
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "null":
        return value is None
    if isinstance(value, bool):
        return False
    if name == "integer":
        return isinstance(value, int)
    return isinstance(value, (int, float))


def _resolve(root, ref):
    node = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise SchemaError("unresolved reference %r" % ref)
        node = node[part]
    return node


def _pointer(path, token):
    return "%s/%s" % (path, str(token).replace("~", "~0").replace("/", "~1"))


def _validate(value, schema, root, path, errors):
    if schema is True:
        return
    if schema is False:
        errors.append(ValidationError(path, "type", {"expected": "nothing"}))
        return
    if "$ref" in schema:
        _validate(value, _resolve(root, schema["$ref"]), root, path, errors)

    def add(code, **params):
        errors.append(ValidationError(path, code, params))

    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(value, n) for n in names):
            add("type", expected="/".join(names))
            return
    if "enum" in schema and value not in schema["enum"]:
        add("enum", allowed=", ".join(json.dumps(v) for v in schema["enum"]))
    if "const" in schema and value != schema["const"]:
        add("const", expected=json.dumps(schema["const"]))

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            add("minLength", limit=schema["minLength"])
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            add("maxLength", limit=schema["maxLength"])
        if "pattern" in schema and not re.search(schema["pattern"], value):
            add("pattern", pattern=schema["pattern"])

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            add("minimum", limit=schema["minimum"])
        if "maximum" in schema and value > schema["maximum"]:
            add("maximum", limit=schema["maximum"])

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            add("minItems", limit=schema["minItems"])
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            add("maxItems", limit=schema["maxItems"])
        if "items" in schema:
            for i, item in enumerate(value):
                _validate(item, schema["items"], root, _pointer(path, i), errors)

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                add("required", name=name)
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            add("minProperties", limit=schema["minProperties"])
        if "propertyNames" in schema:
            for key in value:
                sub = []
                _validate(key, schema["propertyNames"], root, path, sub)
                if sub:
                    pat = sub[0].params.get("pattern", "")
                    errors.append(
                        ValidationError(
                            _pointer(path, key), "propertyNames",
                            {"name": key, "pattern": pat},
                        )
                    )
        extra = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in props:
                _validate(item, props[key], root, _pointer(path, key), errors)
            elif extra is False:
                errors.append(
                    ValidationError(_pointer(path, key), "additionalProperties", {"name": key})
                )
            elif extra is not True:
                _validate(item, extra, root, _pointer(path, key), errors)


def validate(instance, schema: dict) -> list:
    errors = []
    _validate(instance, schema, schema, "", errors)
    return errors


def format_error(err: ValidationError, lang: str | None = None) -> str:
    path = err.path or "/"
    return i18n.t("schema." + err.code, lang, path=path, **err.params)
