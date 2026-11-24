"""Build Chinese plugin packages from the upstream overlay."""
from __future__ import annotations

import argparse
import copy
import json

from common import (
    DIST_DIR,
    ROOT,
    download,
    extract_package,
    find_package_dir,
    get_path,
    load_json,
    lock_data,
    plugin_configs,
    release_by_tag,
    repack,
    safe_extract,
    save_json,
    set_path,
    sha256_bytes,
    sha256_file,
    translation_path,
    translatable_paths,
)


def build_one(cfg: dict, entry: dict, dist_root) -> dict:
    pid = cfg["id"]
    release = release_by_tag(cfg["repo"], entry["tag"])
    asset = next((a for a in release["assets"] if a["name"] == entry["asset"]), None)
    if asset is None:
        raise RuntimeError(f"Asset {entry['asset']} missing from release {entry['tag']}")

    work = ROOT / ".work" / pid / "build"
    archive = work / asset["name"]
    download(asset["browser_download_url"], archive)
    if sha256_file(archive) != entry["asset_sha256"]:
        raise RuntimeError(f"{pid}: upstream archive hash mismatch")

    unpacked = extract_package(archive, work, cfg.get("inner_zip"))
    package_dir = find_package_dir(unpacked, cfg.get("package_dir"), cfg["id"])
    package = unpacked / package_dir
    manifest_path = package / "plugin.json"
    original = load_json(manifest_path)

    wasm_path = package / original["runtime"]["module"]
    if sha256_file(wasm_path) != entry["wasm_sha256"]:
        raise RuntimeError(f"{pid}: wasm changed after lock")

    translation = load_json(translation_path(cfg))
    strings = translation.get("strings", {})
    meta = translation.get("_meta", {})
    revision = meta.get("revision", 1)

    translated = copy.deepcopy(original)
    for key, text in strings.items():
        set_path(translated, key, text)

    allowed = set(translatable_paths(original))
    touched = [
        key for key in strings
        if key in allowed and get_path(original, key) != get_path(translated, key)
    ]
    unexpected = [key for key in strings if key not in allowed]
    if unexpected:
        raise RuntimeError(f"{pid}: translation touched non-translatable fields: {unexpected}")

    missing = [key for key in touched if not strings[key].strip()]
    if missing:
        raise RuntimeError(f"{pid}: empty translations: {missing}")

    for key, limit in (("name", 80), ("description", 240)):
        if len(translated.get(key, "")) > limit:
            raise RuntimeError(f"{pid}: {key} exceeds {limit} characters")
    serialized = json.dumps(translated, ensure_ascii=False, separators=(",", ":"))
    original_size = len(
        json.dumps(original, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    limit = max(16 * 1024, original_size + 1024)
    if len(serialized.encode("utf-8")) > limit:
        raise RuntimeError(f"{pid}: manifest grew beyond {limit} bytes")
    manifest_path.write_text(serialized, encoding="utf-8")

    version = f"{original['version']}-zh.{revision}"
    out_dir = dist_root / pid
    zip_path = out_dir / f"{pid}-{version}.zip"
    repack(package, package_dir, zip_path)

    covered = len([k for k in allowed if strings.get(k)])
    report = {
        "id": pid,
        "upstream": cfg["repo"],
        "upstream_tag": entry["tag"],
        "upstream_asset": entry["asset"],
        "version": version,
        "locale": meta.get("locale", "zh-CN"),
        "upstream_asset_sha256": entry["asset_sha256"],
        "wasm_sha256_upstream": entry["wasm_sha256"],
        "wasm_sha256_build": sha256_file(wasm_path),
        "manifest_sha256_upstream": entry["manifest_sha256"],
        "manifest_sha256_build": sha256_bytes(
            json.dumps(translated, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ),
        "translated": covered,
        "translatable": len(allowed),
        "coverage": round(covered / len(allowed), 4) if allowed else 0,
        "untranslated": sorted(allowed - set(strings)),
        "changed_keys": sorted(touched),
        "package": zip_path.relative_to(ROOT).as_posix(),
        "package_sha256": sha256_file(zip_path),
    }
    save_json(out_dir / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="build every registered plugin")
    parser.add_argument("ids", nargs="*", help="explicit plugin ids to build")
    args = parser.parse_args()

    lock = lock_data()
    targets = plugin_configs()
    if not args.all and args.ids:
        wanted = set(args.ids)
        targets = [cfg for cfg in targets if cfg["id"] in wanted]
        missing = wanted - {cfg["id"] for cfg in targets}
        if missing:
            raise SystemExit(f"Unknown plugin ids: {sorted(missing)}")

    reports = []
    failures = []
    for cfg in targets:
        entry = lock["plugins"].get(cfg["id"])
        if entry is None:
            failures.append({"id": cfg["id"], "error": "no lock entry; run sync.py first"})
            continue
        try:
            reports.append(build_one(cfg, entry, DIST_DIR))
        except Exception as error:
            failures.append({"id": cfg["id"], "error": str(error)})

    lines = ["# 中文插件包", "", "执行代码与上游完全一致，仅 `plugin.json` 的展示文本经过汉化。", ""]
    for report in reports:
        lines.append(
            f"- `{report['id']}` {report['version']} · 上游 {report['upstream_tag']} · "
            f"译文覆盖 {report['coverage']:.0%}"
        )
        lines.append(f"  - wasm SHA-256：`{report['wasm_sha256_build']}`（与上游一致）")
        lines.append(f"  - 安装包：`{report['package']}`")
        if report["untranslated"]:
            lines.append(f"  - 未翻译字段：{', '.join(report['untranslated'])}")
    (DIST_DIR / "RELEASE_NOTES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    save_json(DIST_DIR / "reports.json", {"reports": reports, "failures": failures})

    print(json.dumps({"reports": reports, "failures": failures}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
