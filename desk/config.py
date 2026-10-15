"""Paths, settings and small helpers shared by the desk. Settings come from the environment or .env (gitignored)."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent
STUDIES = ROOT / "studies"
CACHE = ROOT / ".cache"
ENV_FILE = ROOT / ".env"


def _load_env() -> dict[str, str]:
    """Read .env without exporting it to child processes. Values in the real environment win."""
    out: dict[str, str] = {}
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


_ENV = _load_env()


def setting(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name) or _ENV.get(name) or default


DATABANK_ROOT = Path(setting("DATABANK_ROOT", "~/Documents/Data/Data bank")).expanduser()
WAREHOUSE = DATABANK_ROOT / "data" / "warehouse" / "source_native"
PORTAL_ROOT = Path(setting("PORTAL_ROOT", str(ROOT.parent / "Markets data portal"))).expanduser()
PORTAL_DERIVED = PORTAL_ROOT / ".cache" / "derived"
INR_PER_USD = float(setting("INR_PER_USD", "88"))
CAP_INR_PER_STUDY = float(setting("CAP_INR_PER_STUDY", "250"))


def study_dir(slug: str) -> Path:
    d = STUDIES / slug
    if not d.is_dir():
        raise SystemExit(f"no study folder {d}")
    return d


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while b := f.read(chunk):
            h.update(b)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scrub(text: str) -> str:
    """Remove local paths from text that will be committed to the public repo."""
    for root, label in ((str(ROOT), "."), (str(DATABANK_ROOT), "<databank>"), (str(PORTAL_ROOT), "<portal>"),
                        (str(Path.home()), "~")):
        text = text.replace(root, label)
    return text


def write_json(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str) + "\n")
    return path


def read_json(path: Path):
    return json.loads(Path(path).read_text())
