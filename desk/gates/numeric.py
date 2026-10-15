"""Numeric gate: every number in the prose must trace to the results bundle, within its printed rounding.

Ported from the portal research bench (research/gates/numeric.py, 2026-10-15), itself ported in spirit from the Economic Atlas checker (pipeline/verify.mjs in that project) and tightened:

- **Explicit facts only.** The allowed numbers are the bundle's declared facts plus its declared
  context numbers (card parameters, citation years, sample years). Nothing is harvested from free
  text, so a structural count cannot launder an invented figure (the Atlas "358%" lesson).
- **Units must agree.** A number followed by %, "points" or "per cent" can only match a percentage
  rendering (a fraction fact x100, or a pct fact). A bare number cannot match a fraction x100, so
  "an alpha of 4.1" fails where "an alpha of 4.1%" passes. A number with "x" matches a ratio, or a
  fraction as a gross multiple (1 + r).
- **Rounding.** A figure printed with d decimals matches a value v when |v - figure| <= 0.5 x 10^-d.
- **Signs.** An explicit sign (+, -, U+2212) must agree with the fact; an unsigned figure matches
  the absolute value ("trailed by 7.0 points" for a difference of -0.070).
- **Qualifiers.** "about/around/roughly/nearly/almost/some/close to/~" allow 5% relative error.
  "over/more than/above/at least" and "under/less than/below/fewer than/at most" are checked as bounds.
- **Number words** two to twenty, and the tens, are checked like digits ("three primary tests").
  "one" is not checked (it is a pronoun too often).
- **Years and dates.** Four-digit years 1900-2099 must be context years or appear in a bundle label;
  ISO dates and YYYY-MM months must appear in labels or context.
- **Names are masked**, not checked: index names (Nifty 500, Smallcap 250), hypothesis labels (H1),
  T+1, FY26, Q3, and any phrase listed in the bundle's ``allow_phrases``.

The report lists every number with the fact keys it matched, so a critic can check that the prose
used the right fact (a match proves the number exists, not that the sentence describes it).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

PCT_UNITS = {"%", "per cent", "percent", "pts", "pt", "points", "point", "percentage points", "percentage point",
             "pp"}
MULT_UNITS = {"×", "x", "times"}
APPROX = r"(?:about|around|roughly|nearly|almost|some|close to|approximately|~)"
UPPER = r"(?:under|less than|below|fewer than|at most|up to)"
LOWER = r"(?:over|more than|above|at least|exceeding|exceeds)"
WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100}
DEFAULT_MASKS = [
    r"\bNifty\s?(?:50|100|200|500|Next 50|Midcap \d+|Smallcap \d+|Microcap \d+|LargeMidcap \d+)(?:\s?(?:TRI|EW))?\b",
    r"\bNifty500(?: Equal Weight| EW)?\b", r"\b(?:Smallcap|Midcap|Microcap|LargeMidcap)\s?\d+\b", r"\bSensex\b",
    r"\b(?:BSE|S&P BSE)\s?\d+\b", r"\bH\d\b", r"\bT\s?\+\s?\d+\b", r"\bFY\s?\d{2,4}\b", r"\bQ[1-4]\b",
    r"\bCY\d{2,4}\b", r"\bPEP\s?\d+\b", r"\b(?:Section|Rule|Regulation)\s\d+\w*\b", r"\bv\d+(?:\.\d+)*\b",
    r"\[\^?\d+\]",          # footnote markers
]
NUM = r"(?:\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)"
SIGN = r"[+\-−]"
UNIT = (r"(?:\s?(?P<unit>%|×|x\b|per ?cent\b|percentage points?\b|points?\b|pts?\b|pp\b|times\b|bps\b"
        r"|lakh crore\b|crore\b|cr\b|lakh\b))?")


@dataclass
class Mention:
    text: str
    value: float
    decimals: int
    sign: str | None          # "+", "-" or None
    unit: str | None
    kind: str                 # number | year | date | word
    qualifier: str | None     # approx | upper | lower | None
    sentence: str
    start: int
    status: str = "unchecked"
    matches: list[str] = field(default_factory=list)


def _strip_markdown(text: str) -> str:
    """Blank out code, URLs, link targets, HTML comments and front matter, keeping offsets."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    for pat in (r"```.*?```", r"<!--.*?-->", r"`[^`\n]*`", r"\]\([^)]*\)", r"https?://\S+", r"\A---\n.*?\n---\n",
                r"\{\{.*?\}\}"):
        text = re.sub(pat, blank, text, flags=re.S)
    return text


def _sentences(text: str) -> list[tuple[int, int]]:
    spans, start = [], 0
    for m in re.finditer(r"(?<=[.!?])\s+(?=[A-Z₹(\"'*\-\d])|\n\s*\n|\n(?=\s*[-*#|])", text):
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(text)))
    return spans


def extract(text: str, masks: list[str] | None = None) -> list[Mention]:
    clean = _strip_markdown(text)
    for pat in DEFAULT_MASKS + list(masks or []):
        clean = re.sub(pat, lambda m: " " * len(m.group(0)), clean, flags=re.I)
    sents = _sentences(clean)

    def sentence_at(i: int) -> str:
        for a, b in sents:
            if a <= i < b:
                return " ".join(text[a:b].split())
        return ""

    out: list[Mention] = []
    taken = [False] * len(clean)

    def take(a, b):
        for i in range(a, b):
            taken[i] = True

    for m in re.finditer(r"\b(19|20)\d{2}-\d{2}(?:-\d{2})?\b", clean):        # ISO dates and months
        out.append(Mention(m.group(0), 0.0, 0, None, None, "date", None, sentence_at(m.start()), m.start()))
        take(m.start(), m.end())
    rng = re.compile(rf"(?P<a>{NUM})\s?(?P<ua>%|×)?\s?[–—-]\s?(?P<b>{NUM}){UNIT}")
    pat = re.compile(rf"(?:(?P<q>{APPROX}|{UPPER}|{LOWER})\s+)?(?P<sign>{SIGN})?\s?(?:₹|Rs\.?\s?)?(?P<num>{NUM}){UNIT}",
                     re.I)
    spans = []
    for m in rng.finditer(clean):        # ranges: "6–7×", "2016–2026", "52% and 86%"
        if any(taken[m.start():m.end()]):
            continue
        a, b = m.group("a"), m.group("b")
        unit = m.group("unit") or m.group("ua")
        for s, numtxt in ((m.start("a"), a), (m.start("b"), b)):
            spans.append((s, numtxt, None, unit, None))
        take(m.start(), m.end())
    for m in pat.finditer(clean):
        if any(taken[m.start("num"):m.end("num")]):
            continue
        before = clean[max(0, m.start("num") - 1):m.start("num")]
        if before and (before.isalpha() or before in "_/"):
            continue                       # part of a name like Nifty500 or COVID19
        after = clean[m.end("num"):m.end("num") + 2]
        if re.match(r"(?:st|nd|rd|th)\b", after):
            continue                       # ordinals
        if after[:1].isalpha() and not m.group("unit"):
            continue                       # "3y", "5Y", "10k": tokens, not prose figures
        sign = m.group("sign")
        if sign:
            prev = clean[max(0, m.start("sign") - 1):m.start("sign")]
            if prev and (prev.isalnum()):
                sign = None                # a hyphen inside a word, not a sign
        q = m.group("q")
        spans.append((m.start("num"), m.group("num"), sign, m.group("unit"), q))
        take(m.start(), m.end())
    for s, numtxt, sign, unit, q in spans:
        raw = numtxt.replace(",", "")
        val = float(raw)
        dec = len(raw.split(".")[1]) if "." in raw else 0
        unit_n = unit.lower().strip() if unit else None
        if unit_n in ("per cent", "percent"):
            unit_n = "%"
        qual = None
        if q:
            ql = q.lower()
            qual = "approx" if re.fullmatch(APPROX, ql) else "upper" if re.fullmatch(UPPER, ql) else "lower"
        kind = "year" if (dec == 0 and not unit_n and not sign and 1900 <= val <= 2099 and "," not in numtxt) else "number"
        sg = None if not sign else ("+" if sign == "+" else "-")
        out.append(Mention(numtxt if not sign else sign + numtxt, val, dec, sg, unit_n, kind, qual, sentence_at(s), s))
    for m in re.finditer(r"\b(" + "|".join(WORDS) + r")(?:[- ](two|three|four|five|six|seven|eight|nine))?\b",
                         clean, re.I):
        w = m.group(1).lower()
        v = WORDS[w] + (WORDS[m.group(2).lower()] if m.group(2) else 0)
        if w == "hundred":
            continue
        nxt = clean[m.end():m.end() + 12].lower()
        if re.match(r"\s*(?:-|\s)?thirds?|\s*(?:-|\s)?quarters?|\s*(?:-|\s)?fifths?", nxt):
            continue                       # "two-thirds": a fraction word, checked by the critic
        out.append(Mention(m.group(0), float(v), 0, None, None, "word", None, sentence_at(m.start()), m.start()))
    return sorted(out, key=lambda x: x.start)


# ---------------------------------------------------------------- matching

def _renderings(value: float, unit: str) -> list[tuple[float, str]]:
    """(number, family) pairs a fact may appear as. family: pct | mult | plain."""
    if unit == "fraction":
        return [(value * 100, "pct"), (1 + value, "mult"), (value, "plain_fraction")]
    if unit == "pct":
        return [(value, "pct")]
    if unit == "ratio":
        return [(value, "plain"), (value, "mult")]
    if unit == "crore":
        return [(value, "crore"), (value / 1e5, "lakh crore")]
    if unit == "rupees":
        return [(value, "plain"), (value / 1e5, "lakh"), (value / 1e7, "crore"), (value / 1e12, "lakh crore")]
    return [(value, "plain")]


def _family_ok(m: Mention, fam: str) -> bool:
    u = m.unit
    if u in PCT_UNITS:
        return fam == "pct"
    if u in MULT_UNITS:
        return fam == "mult"
    if u in ("crore", "cr"):
        return fam == "crore"
    if u == "lakh crore":
        return fam == "lakh crore"
    if u == "lakh":
        return fam == "lakh"
    if u == "bps":
        return False                       # basis points need an explicit bps fact (not yet used)
    return fam in ("plain", "plain_fraction")


def _close(m: Mention, v: float) -> bool:
    x = m.value
    if m.sign is not None and v != 0 and (v > 0) != (m.sign == "+"):
        return False
    a = abs(v)
    exact = abs(a - x) <= 0.5 * 10 ** -m.decimals + 1e-9
    if m.qualifier == "approx":
        return abs(a - x) <= max(0.05 * x, 0.5 * 10 ** -m.decimals) + 1e-12
    # Bounds must be tight (within 10%): "more than 500 listings" passes for 529, while "below 0.0167"
    # does not pass for a count of 0. An exact match also passes, because "over" often means "across"
    # ("over 124 months") and "below 0.0167" usually cites a threshold that is itself a context number.
    if m.qualifier == "upper":
        return exact or (0.9 * x <= a < x)
    if m.qualifier == "lower":
        return exact or (x < a <= 1.1 * x)
    return exact


def check(text: str, bundle: dict, ambiguous_over: int = 4) -> dict:
    facts = {k: v for k, v in bundle["facts"].items() if v.get("citable", True)}
    context = bundle.get("context_numbers", {})
    label_text = " ".join(str(v) for v in bundle.get("labels", {}).values())
    years = {int(v) for v in context.values() if float(v).is_integer() and 1900 <= v <= 2099}
    years |= {int(y) for y in re.findall(r"\b((?:19|20)\d{2})\b", label_text)}
    mentions = extract(text, bundle.get("allow_phrases", []))
    failures, warnings = [], []
    for m in mentions:
        if m.kind == "date":
            ok = m.text in label_text or m.text in {str(v) for v in context.values()}
            m.status, m.matches = ("ok", ["label"]) if ok else ("fail", [])
        elif m.kind == "year":
            m.status, m.matches = ("ok", ["year"]) if int(m.value) in years else ("fail", [])
        else:
            hits = []
            for key, f in facts.items():
                for num, fam in _renderings(f["value"], f["unit"]):
                    if _family_ok(m, fam) and _close(m, num):
                        hits.append(key)
                        break
            for key, v in context.items():
                if m.unit not in PCT_UNITS | MULT_UNITS and _close(m, v):
                    hits.append(f"context:{key}")
            m.matches = hits
            m.status = "ok" if hits else "fail"
            if m.kind == "word" and not hits:
                m.status = "fail"
            if len(hits) > ambiguous_over:
                warnings.append({"text": m.text, "sentence": m.sentence, "why": f"matches {len(hits)} facts; the "
                                 "claims critic must confirm the sentence uses the right one"})
        if m.status == "fail":
            failures.append({"text": m.text, "kind": m.kind, "unit": m.unit, "sentence": m.sentence,
                             "why": "no fact, context number or label matches this figure at its printed precision"})
    return {"gate": "numeric", "ok": not failures, "checked": len(mentions), "failures": failures,
            "warnings": warnings, "mentions": [asdict(m) for m in mentions]}
