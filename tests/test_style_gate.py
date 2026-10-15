import pytest

from desk.gates.style import check


def rules(text, severity="error"):
    rep = check(text)
    return sorted({f["rule"] for f in (rep["errors"] if severity == "error" else rep["warnings"])})


@pytest.mark.parametrize("text,rule", [
    ("Returns were — as it turns out — flat.", "em_dash_chain"),
    ("Returns were -- in short -- flat.", "double_hyphen_dash"),
    ("This is not luck but skill.", "not_x_but_y"),
    ("The IPO is not just a stock, but a story.", "not_x_but_y"),
    ("The market isn't a casino; it's a voting machine.", "isnt_its"),
    ("Not only did it rise, but also it held.", "not_only_but_also"),
    ("The result? Nothing at all.", "reveal_question"),
    ("In this post we look at IPOs.", "meta_opening"),
    ("Let's dive into the data.", "meta_opening"),
    ("Great question, here it is.", "assistant_voice"),
    ("IPOs rose 6%!", "exclamation"),
    ("IPOs rose 🚀 fast.", "emoji"),
    ("We delve into a rich tapestry of listings.", "ai_vocabulary"),
    ("This underscores the pivotal role of timing.", "ai_vocabulary"),
    ("It's worth noting that alpha was positive.", "filler_hedge"),
    ("This may potentially matter.", "filler_hedge"),
])
def test_error_rules_fire(text, rule):
    assert rule in rules(text)


@pytest.mark.parametrize("text,rule", [
    ("We analyze the annualized data.", "american_spelling"),
    ("They raised ₹500 million.", "western_units"),
    ("Moreover, the median fell.", "connective_padding"),
    ("The gap was very large.", "intensifier"),
    ("One dash — here.", "single_em_dash"),
])
def test_warning_rules_fire(text, rule):
    assert rule in rules(text, "warn")


def test_plain_prose_passes():
    text = ("Indian IPOs since 2016 show no reliable lag behind the market. The typical listing still trails the "
            "index, while a few large winners lift the average. It was not significant, but it points the same way "
            "as the original study. Every number in this post was checked against the results file.")
    rep = check(text)
    assert rep["ok"], rep["errors"]


def test_code_is_ignored():
    assert check("Text.\n\n```python\nx = 1  # not this but that!\n```\n")["ok"]
