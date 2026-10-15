"""The desk's two paid model calls, through each provider's OpenAI-compatible endpoint, with a spend ledger
and a hard per-study cap.

Roles are fixed: `recompute` (DeepSeek) writes an independent script; `review` (Google) reviews and
cold-reads the draft. Both are a different family from the session that writes the study (Claude), which
is the point. Prices are USD per million tokens, read from the providers' pages on 2026-10-07; re-read
them before changing a model. Keys are read from the environment or .env and never logged.
"""

from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import CAP_INR_PER_STUDY, INR_PER_USD, setting

PROVIDERS = {
    "deepseek": {"base_url": "https://api.deepseek.com", "key_env": "DEEPSEEK_API_KEY"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "key_env": "GEMINI_API_KEY"},
}

ROLES = {
    "recompute": {"provider": "deepseek", "model": "deepseek-flash", "max_tokens": 32000,
                  "price": {"input": 0.30, "output": 1.20},
                  "extra": {"thinking": {"type": "enabled"}, "reasoning_effort": "high"}},
    "review": {"provider": "gemini", "model": "gemini-3.8-flash", "max_tokens": 32000,
               "price": {"input": 0.75, "output": 3.75},
               "extra": {"reasoning_effort": "high"}},
}


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Reply:
    text: str
    model: str
    usd: float
    inr: float
    tokens_in: int
    tokens_out: int


def spent_inr(study: Path) -> float:
    ledger = study / "checks" / "costs.jsonl"
    if not ledger.is_file():
        return 0.0
    return sum(json.loads(line)["inr"] for line in ledger.read_text().splitlines() if line.strip())


def _estimate_inr(role: dict, messages: list[dict]) -> float:
    chars = sum(len(m["content"]) for m in messages)
    usd = (chars / 3.5) / 1e6 * role["price"]["input"] + role["max_tokens"] / 1e6 * role["price"]["output"]
    return usd * INR_PER_USD


def complete(study: Path, role_name: str, messages: list[dict], json_mode: bool = False, purpose: str = "") -> Reply:
    """One call, refused if the worst case would take the study past its cap. Logged to checks/costs.jsonl."""
    role = ROLES[role_name]
    prov = PROVIDERS[role["provider"]]
    key = setting(prov["key_env"])
    if not key:
        raise SystemExit(f"{prov['key_env']} is not set (put it in .env)")
    spent, worst = spent_inr(study), _estimate_inr(role, messages)
    if spent + worst > CAP_INR_PER_STUDY:
        raise BudgetExceeded(f"{study.name}: ₹{spent:.0f} spent; this call could cost up to ₹{worst:.0f}; "
                             f"cap ₹{CAP_INR_PER_STUDY:.0f}")
    body = {"model": role["model"], "messages": messages, "max_tokens": role["max_tokens"], **role["extra"]}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(prov["base_url"].rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    data = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                data = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 4:
                raise RuntimeError(f"{role['provider']} HTTP {e.code}: {e.read()[:500]!r}") from None
        except (urllib.error.URLError, TimeoutError):
            if attempt == 4:
                raise
        time.sleep(2 ** attempt + random.random())
    usage = data.get("usage", {})
    tin, tout = int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))
    usd = tin / 1e6 * role["price"]["input"] + tout / 1e6 * role["price"]["output"]
    reply = Reply(data["choices"][0]["message"].get("content") or "", data.get("model", role["model"]), usd,
                  usd * INR_PER_USD, tin, tout)
    ledger = study / "checks" / "costs.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as f:
        f.write(json.dumps({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "role": role_name,
                            "purpose": purpose, "model": reply.model, "tokens_in": tin, "tokens_out": tout,
                            "usd": round(usd, 5), "inr": round(reply.inr, 2)}) + "\n")
    return reply
