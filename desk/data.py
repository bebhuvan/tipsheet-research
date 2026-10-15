"""Read-only access to the two input stores, with a fingerprint of every file a study reads.

    databank:<dataset>   the newest Parquet snapshot in the Data bank warehouse (DATABANK_ROOT)
    portal:<table>       a table the portal pipeline derives (PORTAL_ROOT/.cache/derived/<table>.parquet)

Nothing here writes to either store, and no portal code is imported. Fingerprints (path, size, mtime,
sha256) go into results.json so `desk check` can tell when results were computed on data that has
since changed. Hashes are cached by (path, size, mtime) because some inputs are several GB.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import CACHE, PORTAL_DERIVED, WAREHOUSE, sha256_file

_HASH_CACHE = CACHE / "fingerprints.json"


def resolve(name: str) -> Path:
    store, _, key = name.partition(":")
    if store == "databank":
        folder = WAREHOUSE / key
        files = sorted(folder.glob("*.parquet"), key=lambda p: p.stat().st_mtime) if folder.is_dir() else []
        if not files:
            raise FileNotFoundError(f"no warehouse snapshot for {key} under {WAREHOUSE}")
        return files[-1]
    if store == "portal":
        p = PORTAL_DERIVED / (key if key.endswith(".parquet") else f"{key}.parquet")
        if not p.is_file():
            raise FileNotFoundError(f"no portal table {p}")
        return p
    raise ValueError(f"input name must start with databank: or portal:, got {name!r}")


def fingerprint(path: Path) -> dict:
    st = path.stat()
    key = f"{path}|{st.st_size}|{st.st_mtime_ns}"
    cache = json.loads(_HASH_CACHE.read_text()) if _HASH_CACHE.is_file() else {}
    if key not in cache:
        cache[key] = sha256_file(path)
        _HASH_CACHE.parent.mkdir(parents=True, exist_ok=True)
        _HASH_CACHE.write_text(json.dumps(cache, indent=0))
    return {"path": str(path), "size": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": cache[key]}


def load(name: str, results=None, columns: list[str] | None = None, filters=None) -> pd.DataFrame:
    """Load an input as a DataFrame and record its fingerprint in `results` (a desk.results.Results)."""
    path = resolve(name)
    if results is not None:
        results.input(name, fingerprint(path))
    return pd.read_parquet(path, columns=columns, filters=filters)


def path_of(name: str, results=None) -> Path:
    """The file behind an input, for reading with DuckDB. Records the fingerprint like load()."""
    path = resolve(name)
    if results is not None:
        results.input(name, fingerprint(path))
    return path


def changed_inputs(recorded: dict[str, dict]) -> list[str]:
    """Inputs whose file is missing, has been replaced by a newer snapshot, or whose content changed."""
    out = []
    for name, fp in recorded.items():
        try:
            now = resolve(name)
        except FileNotFoundError:
            out.append(f"{name}: missing")
            continue
        if str(now) != fp["path"]:
            out.append(f"{name}: newer snapshot {now.name}")
            continue
        st = now.stat()
        if st.st_size == fp["size"] and st.st_mtime_ns == fp["mtime_ns"]:
            continue
        if fingerprint(now)["sha256"] != fp["sha256"]:
            out.append(f"{name}: content changed")
    return out
