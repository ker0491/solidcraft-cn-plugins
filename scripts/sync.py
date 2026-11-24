"""Detect upstream plugin releases and refresh upstream.lock.json."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from common import (
    ROOT,
    download,
    extract_package,
    find_package_dir,
    latest_release,
    lock_data,
    pick_asset,
    plugin_configs,
    save_json,
    sha256_file,
)

TRACKED = ("tag", "asset", "asset_sha256", "manifest_sha256", "wasm_sha256")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="*", help="only sync these plugin ids")
    args = parser.parse_args()

    lock = lock_data()
    changes = []
    configs = plugin_configs()
    if args.ids:
        wanted = set(args.ids)
        configs = [cfg for cfg in configs if cfg["id"] in wanted]

    failures = []
    for cfg in configs:
        try:
            release = latest_release(cfg["repo"])
            asset = pick_asset(release, cfg["asset_pattern"])
            tag = release["tag_name"]

            work = ROOT / ".work" / cfg["id"] / "sync"
            archive = work / asset["name"]
            download(asset["browser_download_url"], archive)

            unpacked = extract_package(archive, work, cfg.get("inner_zip"))
            package = unpacked / find_package_dir(unpacked, cfg.get("package_dir"), cfg["id"])
            manifest = package / "plugin.json"
            wasm_name = json.loads(manifest.read_text(encoding="utf-8"))["runtime"]["module"]

            record = {
                "tag": tag,
                "asset": asset["name"],
                "asset_sha256": sha256_file(archive),
                "manifest_sha256": sha256_file(manifest),
                "wasm_sha256": sha256_file(package / wasm_name),
                "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }

            previous = lock["plugins"].get(cfg["id"])
            if previous is None or any(previous.get(k) != record[k] for k in TRACKED):
                changes.append({"id": cfg["id"], "previous": previous, "current": record})
            lock["plugins"][cfg["id"]] = record
        except Exception as error:
            failures.append({"id": cfg["id"], "error": str(error)})

    save_json(ROOT / "upstream.lock.json", lock)
    print(json.dumps({"changes": changes, "failures": failures}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
