#!/usr/bin/env python3
"""Extrae los widget_type de un export de ThingsBoard Version Control a archivos
legibles (html/css/js/json) para revisión con números de línea.

Solo lee el directorio de configuración; nunca lo modifica.

Uso:
    python3 -I qa/scripts/extract_widgets.py \
        --config ../sunkuu-tb-config --out qa/extract [--include-dev]

Salida (por widget, carpeta = fqn):
    qa/extract/<fqn>/templateHtml.html
    qa/extract/<fqn>/templateCss.css
    qa/extract/<fqn>/controllerScript.js
    qa/extract/<fqn>/settingsForm.json, defaultConfig.json, resources.json, ...
    qa/extract/<fqn>/meta.json        (id, nombre, fqn, archivo fuente, commit)
    qa/extract/MANIFEST.json          (commit analizado + lista de widgets)
"""
import argparse
import json
import os
import subprocess
import sys

TEXT_FIELDS = {
    "templateHtml": "templateHtml.html",
    "templateCss": "templateCss.css",
    "controllerScript": "controllerScript.js",
}


def git_head(config_dir):
    try:
        out = subprocess.run(
            ["git", "-C", config_dir, "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def is_dev(entity):
    name = (entity.get("name") or "").upper()
    fqn = (entity.get("fqn") or "").lower()
    return name.endswith(" DEV") or fqn.endswith("_dev")


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        if content and not content.endswith("\n"):
            f.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True, help="ruta a sunkuu-tb-config")
    ap.add_argument("--out", required=True, help="directorio de salida (p. ej. qa/extract)")
    ap.add_argument("--include-dev", action="store_true", help="incluir copias DEV")
    args = ap.parse_args()

    config_dir = os.path.abspath(args.config)
    out_dir = os.path.abspath(args.out)
    if out_dir.startswith(config_dir + os.sep) or out_dir == config_dir:
        sys.exit("ERROR: --out no puede estar dentro del directorio de configuración")

    wt_dir = os.path.join(config_dir, "widget_type")
    commit = git_head(config_dir)
    os.makedirs(out_dir, exist_ok=True)
    manifest = {"config_commit": commit, "widgets": [], "skipped": []}

    for fname in sorted(os.listdir(wt_dir)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(wt_dir, fname), encoding="utf-8") as f:
            entity = json.load(f)["entity"]
        info = {"id": fname[:-5], "name": entity.get("name"), "fqn": entity.get("fqn")}
        if is_dev(entity) and not args.include_dev:
            manifest["skipped"].append({**info, "reason": "DEV"})
            continue

        wdir = os.path.join(out_dir, entity.get("fqn") or info["id"])
        os.makedirs(wdir, exist_ok=True)
        desc = entity.get("descriptor") or {}
        for key, value in desc.items():
            if key in TEXT_FIELDS:
                write(os.path.join(wdir, TEXT_FIELDS[key]), value or "")
            elif isinstance(value, (dict, list)):
                write(os.path.join(wdir, key + ".json"), json.dumps(value, indent=2, ensure_ascii=False))
            elif isinstance(value, str) and key in ("defaultConfig", "settingsForm"):
                try:
                    parsed = json.loads(value)
                    write(os.path.join(wdir, key + ".json"), json.dumps(parsed, indent=2, ensure_ascii=False))
                except ValueError:
                    write(os.path.join(wdir, key + ".txt"), value)
        meta = {**info, "source": os.path.join("widget_type", fname), "config_commit": commit,
                "descriptor_scalars": {k: v for k, v in desc.items()
                                       if not isinstance(v, (dict, list)) and k not in TEXT_FIELDS
                                       and k not in ("defaultConfig", "settingsForm")}}
        write(os.path.join(wdir, "meta.json"), json.dumps(meta, indent=2, ensure_ascii=False))
        manifest["widgets"].append(info)

    write(os.path.join(out_dir, "MANIFEST.json"), json.dumps(manifest, indent=2, ensure_ascii=False))
    print("commit:", commit)
    for w in manifest["widgets"]:
        print("  extraído:", w["fqn"], "-", w["name"])
    for w in manifest["skipped"]:
        print("  omitido :", w["fqn"], "-", w["name"], "(" + w["reason"] + ")")


if __name__ == "__main__":
    main()
