"""Shared helpers for the SolidCraft Chinese plugin overlay."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import shutil
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"
TRANSLATIONS_DIR = ROOT / "translations"
LOCK_PATH = ROOT / "upstream.lock.json"
DIST_DIR = ROOT / "dist"
WORK_DIR = ROOT / ".work"
API_BASE = "https://api.github.com"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def api_get(path: str) -> Any:
    last_error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                f"{API_BASE}{path}",
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "solidcraft-cn-plugins",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            token = os.environ.get("GITHUB_TOKEN")
            if token:
                req.add_header("Authorization", f"Bearer {token}")
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except Exception as error:
            last_error = error
            if attempt < 2:
                time.sleep(1)
    raise last_error


def latest_release(repo: str) -> dict[str, Any]:
    return api_get(f"/repos/{repo}/releases/latest")


def release_by_tag(repo: str, tag: str) -> dict[str, Any]:
    return api_get(f"/repos/{repo}/releases/tags/{tag}")


def pick_asset(release: dict[str, Any], pattern: str) -> dict[str, Any]:
    assets = release.get("assets", [])
    for asset in assets:
        if asset["name"] == pattern:
            return asset
    for asset in assets:
        if fnmatch.fnmatch(asset["name"], pattern):
            return asset
    raise RuntimeError(f"No asset matching {pattern!r} in {release.get('tag_name')}")


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "solidcraft-cn-plugins"})
            with urllib.request.urlopen(req, timeout=60) as resp, dest.open("wb") as f:
                shutil.copyfileobj(resp, f)
            return
        except Exception as error:
            last_error = error
            if attempt < 2:
                time.sleep(1)
    raise last_error


def extract_package(archive: Path, work_dir: Path, inner_zip: str | None = None) -> Path:
    unpacked = work_dir / "unpacked"
    safe_extract(archive, unpacked)
    if inner_zip:
        inner = unpacked / inner_zip
        target = work_dir / "inner"
        safe_extract(inner, target)
        return target
    return unpacked


def find_package_dir(
    unpacked: Path, preferred: str | None = None, expected_id: str | None = None
) -> str:
    candidates = []
    for path in sorted(unpacked.rglob("plugin.json")):
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if not isinstance(manifest, dict) or not isinstance(manifest.get("runtime"), dict):
            continue
        if not manifest.get("id"):
            continue
        directory = path.parent.relative_to(unpacked).as_posix()
        score = 0
        if expected_id and manifest["id"] == expected_id:
            score += 2
        if preferred and directory == preferred:
            score += 1
        candidates.append((score, directory))
    if not candidates:
        raise RuntimeError("No valid plugin.json found in extracted package")
    return max(candidates)[1]


def safe_extract(zip_path: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    root = dest.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            target = (dest / info.filename).resolve()
            if target != root and not str(target).startswith(str(root) + os.sep):
                raise RuntimeError(f"Unsafe path in zip: {info.filename}")
        zf.extractall(dest)


def repack(source_dir: Path, root: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    files = [path for path in source_dir.rglob("*") if path.is_file()]
    files.sort(key=lambda path: (path.name != "plugin.json", path.as_posix()))
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, f"{root}/{path.relative_to(source_dir).as_posix()}")


def plugin_configs() -> list[dict[str, Any]]:
    configs = []
    for cfg_path in sorted(PLUGINS_DIR.glob("*/upstream.json")):
        cfg = load_json(cfg_path)
        cfg["_path"] = cfg_path
        configs.append(cfg)
    return configs


def translation_path(cfg: dict[str, Any]) -> Path:
    return ROOT / cfg["translation"]


def lock_data() -> dict[str, Any]:
    if LOCK_PATH.exists():
        return load_json(LOCK_PATH)
    return {"format": 1, "plugins": {}}


def _locate(obj: Any, parts: list[str], create: bool = False) -> tuple[Any, str]:
    cur = obj
    for part in parts[:-1]:
        if isinstance(cur, list):
            if part.isdigit():
                index = int(part)
                if index >= len(cur) and create:
                    raise KeyError("Cannot append to list via path")
                cur = cur[index]
            else:
                cur = next(
                    (x for x in cur if isinstance(x, dict) and x.get("name") == part),
                    None,
                )
        elif isinstance(cur, dict):
            if part not in cur:
                if create:
                    cur[part] = {}
                else:
                    raise KeyError(".".join(parts))
            cur = cur[part]
        else:
            raise KeyError(".".join(parts))
        if cur is None:
            raise KeyError(".".join(parts))
    return cur, parts[-1]


def _parts(dotted: str) -> list[str]:
    parts = dotted.split(".")
    if parts[0] == "entries":
        parts = ["runtime"] + parts
    if "input_schema" in parts:
        index = parts.index("input_schema")
        if index + 1 < len(parts) and parts[index + 1] != "properties":
            parts = parts[: index + 1] + ["properties"] + parts[index + 1 :]
    return parts


def get_path(obj: Any, dotted: str) -> Any:
    parent, key = _locate(obj, _parts(dotted))
    if isinstance(parent, list) and key.isdigit():
        return parent[int(key)]
    return parent[key]


def set_path(obj: Any, dotted: str, value: str) -> None:
    parent, key = _locate(obj, _parts(dotted), create=True)
    if isinstance(parent, list) and key.isdigit():
        parent[int(key)] = value
    else:
        parent[key] = value


def translatable_paths(manifest: dict[str, Any]) -> list[str]:
    paths = [key for key in ("name", "description") if key in manifest]
    for entry in manifest.get("runtime", {}).get("entries", []):
        name = entry.get("name")
        if not name:
            continue
        prefix = f"entries.{name}"
        # The entry name is a program identifier passed to the wasm component
        # via execute(entry, params); translating it would break dispatch.
        properties = entry.get("input_schema", {}).get("properties", {})
        for prop, spec in properties.items():
            for field in ("title", "description"):
                if isinstance(spec, dict) and isinstance(spec.get(field), str):
                    paths.append(f"{prefix}.input_schema.{prop}.{field}")
    return paths
