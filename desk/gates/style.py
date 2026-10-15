"""Style gate: an AI-pattern linter for the owner's house style (plain Indian English, no AI tells).

Errors fail the gate; warnings go to the writer's revision prompt and the final reviewer. The rules
come from the owner's global preferences (no em-dash chains, no "not X but Y" flourishes, no filler
hedges, no meta decoration) and the writing-voice skill. Each rule is a regex over prose with code,
URLs and front matter removed; matches report line numbers and the offending text.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .numeric import _strip_markdown


@dataclass
class Rule:
    id: str
    severity: str        # error | warn
    pattern: str
    message: str
    flags: int = re.I


def _words(*ws: str) -> str:
    return r"\b(?:" + "|".join(ws) + r")\b"


RULES = [
    # --- structure tells
    Rule("em_dash_chain", "error", r"[^.!?\n]*—[^.!?\n]*—[^.!?\n]*",
         "Two or more em dashes in one sentence. Use a full stop, a comma or brackets."),
    Rule("double_hyphen_dash", "error", r"\s--\s", "Typed double hyphen used as a dash."),
    # "not luck but skill", "not just a bug, but a feature". X is short and Y is a parallel phrase; a
    # concession with its own clause ("not significant, but it points the same way") is left alone.
    Rule("not_x_but_y", "error",
         r"\bnot (?:just |only |merely |simply |so much )?(?:a |an |the |about |because )?[\w'%.-]+(?:\s[\w'%.-]+){0,4},?"
         r"\s+but (?:rather |instead )?(?!it\b|they\b|we\b|there\b|this\b|that\b|he\b|she\b|i\b|you\b|its\b|their\b)"
         r"(?:a |an |the |about |because )?\w+",
         "A 'not X but Y' construction. State Y plainly."),
    Rule("isnt_its", "error", r"\b(?:isn't|is not|wasn't|aren't)\b[^.;!?\n]{1,60}[;,—–]\s*(?:it's|it is|they're|it was)\b",
         "An 'isn't X; it's Y' reversal."),
    Rule("not_only_but_also", "error", r"\bnot only\b[^.!?\n]{1,80}\bbut also\b", "'Not only ... but also'."),
    Rule("reveal_question", "error",
         r"\b(?:The (?:answer|result|catch|twist|verdict|kicker|upshot|short answer)|Why|What happened|The takeaway)\?\s",
         "A question-then-reveal ('The result? ...'). Say the result."),
    Rule("meta_opening", "error",
         r"(?:^|(?<=[.!?]\s))(?:In this (?:post|article|piece|essay|blog)|This (?:post|article|piece) (?:will|aims|explores|looks)|"
         r"[Ll]et's (?:dive|take a (?:closer |deep )?look|explore|unpack|break (?:it|this) down)|Without further ado)\b",
         "Meta decoration. Start with the finding.", re.M),
    Rule("assistant_voice", "error", r"\b(?:As an AI|I hope this helps|Great question|Certainly!|In conclusion,|In summary,|To sum up,)",
         "Assistant voice."),
    Rule("exclamation", "error", r"!(?!\[)", "Exclamation mark."),
    Rule("emoji", "error", "[\U0001F300-\U0001FAFF☀-➿⭐✅]", "Emoji.", 0),
    # --- vocabulary tells
    Rule("ai_vocabulary", "error",
         _words("delve", "delves", "delving", "tapestry", "testament to", "in the realm of", "ever-evolving",
                "fast-paced world", "game[- ]changer", "embark(?:s|ed)? on", "a myriad of", "plethora",
                "paradigm shift", "seamless(?:ly)?", "synergy", "holistic", "cutting-edge", "unlock(?:s|ing)? the",
                "navigat(?:e|ing) the (?:complexities|landscape|world)", "serves as a (?:reminder|testament)",
                "stands as a", "underscores?", "showcas(?:e|es|ing)", "pivotal", "intricate", "multifaceted",
                "in today's", "rich history", "deep dive", "buckle up", "here's the thing", "the bottom line is",
                "at the end of the day", "needless to say", "it goes without saying"),
         "Stock AI vocabulary."),
    Rule("filler_hedge", "error",
         _words("it's worth noting", "it is worth noting", "it's important to note", "it is important to note",
                "it should be noted", "interestingly,", "importantly,", "notably,", "crucially,", "arguably",
                "it could be argued", "may potentially", "could potentially", "might potentially", "could possibly",
                "may possibly", "to some extent", "in many ways", "a wide range of", "plays a (?:crucial|vital|key) role"),
         "Filler or stacked hedge. Cut it or say how sure we are with a number."),
    Rule("connective_padding", "warn", r"(?:^|(?<=[.!?]\s))(?:Moreover|Furthermore|Additionally|Ultimately|Overall),",
         "Padding connective at the start of a sentence."),
    Rule("intensifier", "warn", _words("very", "really", "extremely", "incredibly", "truly", "remarkably", "hugely"),
         "Intensifier. Use the number instead."),
    Rule("single_em_dash", "warn", r"—", "Em dash. Allowed sparingly; prefer a comma or a full stop."),
    Rule("crucial_words", "warn", _words("crucial", "vital", "key takeaway", "robust(?:ly)?", "landscape", "journey"),
         "Overused word; check it is literal."),
    # --- Indian English conventions
    Rule("american_spelling", "warn",
         _words("analyze[ds]?", "analyzing", "annualized", "annualize", "behavior(?:al|s)?", "color(?:s|ed)?",
                "favor(?:ite|s|ed)?", "center(?:s|ed)?", "modeling", "modeled", "labor", "optimize[ds]?",
                "optimizing", "organization", "realize[ds]?", "recognize[ds]?", "summarize[ds]?", "defense"),
         "American spelling. Indian English follows British spelling (annualised, behaviour, colour)."),
    Rule("western_units", "warn", r"(?:₹|Rs\.?)\s?[\d.,]+\s?(?:million|billion|trillion)\b|\b(?:million|billion)\s+(?:rupees|₹)",
         "Rupee amounts in millions/billions. Use lakh and crore."),
]


def check(text: str, max_sentence_words: int = 45) -> dict:
    prose = _strip_markdown(text)
    lines = prose.splitlines()
    findings = []
    for rule in RULES:
        for m in re.finditer(rule.pattern, prose, rule.flags | re.M):
            line = prose.count("\n", 0, m.start()) + 1
            findings.append({"rule": rule.id, "severity": rule.severity, "line": line,
                             "text": " ".join(m.group(0).split())[:160], "message": rule.message})
    for i, ln in enumerate(lines, 1):            # long sentences (warn)
        if ln.lstrip().startswith(("|", "#", "-", "*")):
            continue
        for s in re.split(r"(?<=[.!?])\s+", ln):
            n = len(s.split())
            if n > max_sentence_words:
                findings.append({"rule": "long_sentence", "severity": "warn", "line": i, "text": s[:120] + "…",
                                 "message": f"{n} words; split it."})
    errors = [f for f in findings if f["severity"] == "error"]
    return {"gate": "style", "ok": not errors, "errors": errors,
            "warnings": [f for f in findings if f["severity"] == "warn"], "rules": [asdict(r) for r in RULES]}
