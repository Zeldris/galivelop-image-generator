#!/usr/bin/env python3
"""Desglose de un registro de gimg para gw-opt-ai (solo stdlib).

Complementa a measure.py de la skill, que agrupa por perfil, tarea y modelo: aquí se agrupa por perfil, modelo,
tamaño, pasos y borrador, y se separan las fases (carga, muestreo, decodificado del VAE), los s/paso y la memoria
libre mínima. Lista también los errores agrupados (primeros 140 caracteres) y los ajustes de memoria de sd-cli.

Uso: python3 .claude/gw/gw-opt-ai-desglose.py <registro.jsonl> [--profile P]
"""
import argparse
import collections
import json
import re
import statistics

MEM_FLAGS = re.compile(
    r"(--(?:max-vram|params-backend|flash-attn|vae-tiling|vae-tile-size|vae-tile-overlap|offload-to-cpu|backend)"
    r"(?: [^-\s]\S*)?)"
)


def seconds(rows, field):
    values = [r[field] for r in rows if isinstance(r.get(field), (int, float))]
    return round(statistics.median(values) / 1000, 1) if values else "-"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log")
    ap.add_argument("--profile")
    args = ap.parse_args()

    rows = []
    with open(args.log, encoding="utf-8") as fh:
        for line in fh:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    if args.profile:
        rows = [r for r in rows if r.get("app.machine_profile") == args.profile]

    groups = collections.defaultdict(list)
    errors = collections.Counter()
    flags = collections.Counter()
    for r in rows:
        key3 = (r.get("app.machine_profile"), r.get("app.task"), r.get("gen_ai.request.model"))
        if r.get("app.error"):
            errors[key3 + (str(r["app.error"])[:140].replace("\n", " | "),)] += 1
            continue
        groups[(r.get("app.machine_profile"), r.get("gen_ai.request.model"), r.get("app.image.width"),
                r.get("app.image.height"), r.get("app.image.steps"), r.get("app.image.draft"),
                bool(r.get("app.image.references")))].append(r)
        cmd = r.get("app.image.command", "")
        cmd = cmd if isinstance(cmd, str) else " ".join(map(str, cmd))
        flags[(r.get("app.machine_profile"), r.get("gen_ai.request.model"), " ".join(MEM_FLAGS.findall(cmd)))] += 1

    print("perfil modelo WxH pasos borrador ref | n | total_s carga_s muestreo_s vae_s | s/paso | min_free_mb")
    for k, rs in sorted(groups.items(), key=lambda kv: str(kv[0])):
        profile, model, w, h, steps, draft, ref = k
        sample = [x["app.image.sample_ms"] for x in rs if isinstance(x.get("app.image.sample_ms"), (int, float))]
        per_step = round(statistics.median(sample) / 1000 / steps, 1) if sample and steps else "-"
        free = [x["app.image.min_free_mb"] for x in rs if isinstance(x.get("app.image.min_free_mb"), (int, float))]
        print(profile, model, f"{w}x{h}", steps, draft, ref, "|", len(rs), "|",
              seconds(rs, "app.duration_ms"), seconds(rs, "app.load_ms"), seconds(rs, "app.image.sample_ms"),
              seconds(rs, "app.image.decode_ms"), "|", per_step, "|", min(free) if free else "-")

    print("\najustes de memoria de sd-cli (n, perfil, modelo, opciones):")
    for k, n in sorted(flags.items(), key=str):
        print(n, *k)

    print("\nerrores (n, perfil, tarea, modelo, mensaje):")
    for k, n in errors.most_common():
        print(n, *k)

    stamps = sorted(r.get("ts", "") for r in rows if r.get("ts"))
    if stamps:
        print("\nrango:", stamps[0], "→", stamps[-1])


if __name__ == "__main__":
    main()
