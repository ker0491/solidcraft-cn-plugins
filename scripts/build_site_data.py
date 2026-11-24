"""Merge the upstream plugin catalog with local translations and localized packages.

The catalog source is tharje/solidcraft-plugins (MIT), whose update.py already discovers
community plugins from GitHub. We reuse its list and only maintain translation files.
"""
from __future__ import annotations

import json
import shutil
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_URL = "https://raw.githubusercontent.com/tharje/solidcraft-plugins/main/data/plugins.json"
CATALOG_CACHE = ROOT / "site" / "data" / "catalog-upstream.json"
SITE_DATA = ROOT / "site" / "data" / "plugins.json"
PACKAGES = ROOT / "site" / "packages"

CATEGORY_ZH = {
    "Storage & organizing": "收纳与整理",
    "Hardware & fasteners": "五金与紧固件",
    "Gears & motion": "齿轮与传动",
    "Woodworking": "木工",
    "Aero & marine": "航空与船舶",
    "Shapes & patterns": "形状与图案",
    "3D printing": "3D 打印",
    "Export & workflow": "导出与工作流",
    "Examples": "官方示例",
    "Other": "其他",
}


def fetch_catalog() -> dict:
    try:
        req = urllib.request.Request(CATALOG_URL, headers={"User-Agent": "solidcraft-cn-plugins"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.load(response)
        CATALOG_CACHE.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return data
    except Exception:
        if CATALOG_CACHE.exists():
            return json.loads(CATALOG_CACHE.read_text(encoding="utf-8"))
        raise RuntimeError("Cannot fetch upstream catalog and no local cache exists")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def main() -> int:
    catalog = fetch_catalog()
    plugins = []

    for source in catalog.get("plugins", []):
        pid = source.get("id")
        slug = source.get("slug") or pid
        if not pid:
            continue

        translation = read_json(ROOT / "translations" / f"{pid}.zh-CN.json") or {}
        report = read_json(ROOT / "dist" / pid / "report.json")
        strings = translation.get("strings", {})
        meta = translation.get("_meta", {})
        release = source.get("release") or {}

        localized_zip = None
        if report:
            package = ROOT / report["package"]
            if package.exists():
                target = PACKAGES / pid / package.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(package, target)
                localized_zip = f"packages/{pid}/{package.name}"

        tested = source.get("tested") or {}
        plugins.append({
            "id": pid,
            "slug": slug,
            "name": strings.get("name") or source.get("name") or pid,
            "nameOriginal": source.get("name") or pid,
            "nameZh": strings.get("name"),
            "description": strings.get("description") or source.get("description") or "",
            "descriptionOriginal": source.get("description") or "",
            "category": CATEGORY_ZH.get(source.get("category"), source.get("category") or "其他"),
            "categoryOriginal": source.get("category") or "",
            "owner": source.get("owner") or "",
            "repo": source.get("repo") or "",
            "url": source.get("url") or f"https://github.com/{source.get('repo', '')}",
            "avatar": source.get("avatar") or "",
            "image": source.get("image"),
            "topics": source.get("topics") or [],
            "stars": source.get("stars") or 0,
            "downloads": source.get("downloads") or 0,
            "updated": source.get("updated"),
            "version": source.get("version"),
            "upstreamTag": release.get("tag"),
            "upstreamZip": release.get("zip"),
            "tested": tested.get("label"),
            "localized": bool(report),
            "localizedVersion": report.get("version") if report else None,
            "localizedZip": localized_zip,
            "wasmSha": report.get("wasm_sha256_build") if report else None,
            "coverage": report.get("coverage") if report else None,
            "revision": meta.get("revision") if translation else None,
        })

    result = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "catalogGenerated": catalog.get("generated"),
        "catalogUrl": CATALOG_URL,
        "total": len(plugins),
        "localized": sum(1 for p in plugins if p["localized"]),
        "downloadable": sum(1 for p in plugins if p["upstreamZip"]),
        "plugins": plugins,
    }
    SITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    SITE_DATA.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "plugins"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
