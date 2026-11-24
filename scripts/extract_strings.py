"""Download upstream plugin zips and extract translatable strings into a backlog."""
from __future__ import annotations

import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, get_path, translatable_paths

CATALOG = ROOT / "site" / "data" / "catalog-upstream.json"
BACKLOG = ROOT / ".work" / "translation-backlog.json"


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    backlog = {}

    for plugin in catalog.get("plugins", []):
        release = plugin.get("release") or {}
        url = release.get("zip")
        if not url:
            continue
        pid = plugin.get("id")
        if not pid:
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "solidcraft-cn-plugins"})
            with urllib.request.urlopen(req, timeout=60) as response:
                archive = response.read()
            zf = zipfile.ZipFile(io.BytesIO(archive))
            manifests = [name for name in zf.namelist() if name.endswith("plugin.json")]
            manifest = None
            for name in manifests:
                candidate = json.loads(zf.read(name))
                if candidate.get("id") == pid:
                    manifest = candidate
                    break
            if manifest is None and manifests:
                manifest = json.loads(zf.read(manifests[0]))
            if not manifest:
                raise RuntimeError("no plugin.json in package")

            paths = translatable_paths(manifest)
            backlog[pid] = {
                "repo": plugin.get("repo"),
                "name": plugin.get("name"),
                "version": plugin.get("version"),
                "stars": plugin.get("stars") or 0,
                "zip": url,
                "fields": {path: get_path(manifest, path) for path in paths},
            }
        except Exception as error:
            backlog[pid] = {"repo": plugin.get("repo"), "error": str(error)}

    BACKLOG.parent.mkdir(parents=True, exist_ok=True)
    BACKLOG.write_text(json.dumps(backlog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ok = {k: v for k, v in backlog.items() if "fields" in v}
    failed = {k: v for k, v in backlog.items() if "error" in v}
    print(json.dumps({
        "packages": len(backlog),
        "extracted": len(ok),
        "failed": failed,
        "total_fields": sum(len(v["fields"]) for v in ok.values()),
        "by_stars": sorted(((k, len(v["fields"]), v["stars"]) for k, v in ok.items()),
                           key=lambda x: -x[2]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
