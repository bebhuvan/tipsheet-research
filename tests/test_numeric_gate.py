from desk.gates.numeric import check, extract

BUNDLE = {
    "facts": {
        "alpha": {"value": 0.04127, "unit": "fraction"},
        "t_alpha": {"value": 0.8912, "unit": "t"},
        "beta": {"value": 1.2215, "unit": "ratio"},
        "n": {"value": 529, "unit": "count"},
        "median_bhar": {"value": -0.0762, "unit": "fraction"},
        "diff": {"value": -0.0702, "unit": "fraction"},
        "share": {"value": 0.4378, "unit": "fraction"},
        "gross": {"value": 10.4, "unit": "fraction"},
        "raised": {"value": 125000.0, "unit": "crore"},
        "structural_count": {"value": 358, "unit": "count", "citable": False},
    },
    "labels": {"first": "2016-06"},
    "context_numbers": {"threshold": 0.0167, "lags": 3, "year.2016": 2016, "year.2026": 2026, "cite": 1991},
}


def failures(text):
    return [f["text"] for f in check(text, BUNDLE)["failures"]]


def test_clean_sentence_passes():
    t = ("Across 529 listings the alpha was +4.1% a year (t = 0.89), with a beta of 1.22. "
         "The median trailed by 7.6 points and 44% beat the index, from 2016-06 to 2026.")
    rep = check(t, BUNDLE)
    assert rep["ok"], rep["failures"]
    assert rep["checked"] >= 7


def test_hallucinated_number_fails():
    assert failures("The alpha was 5.3% a year.") == ["5.3"]


def test_rounding_respects_printed_precision():
    assert not failures("Alpha was 4.13%.")        # 4.127 -> 4.13
    assert not failures("Alpha was 4%.")           # 4.127 -> 4
    assert failures("Alpha was 4.2%.") == ["4.2"]  # wrong at 1 dp


def test_percentage_needs_a_percent_sign():
    # a fraction fact can only appear as a percentage with % or points; a bare 4.1 is a unit slip
    assert failures("Alpha was 4.1 a year.") == ["4.1"]
    assert not failures("Alpha was 4.1% a year.")


def test_explicit_sign_must_agree():
    assert failures("The median gap was +7.6%.") == ["+7.6"]
    assert not failures("The median gap was −7.6%.")     # unicode minus
    assert not failures("The median trailed by 7.6%.")   # unsigned matches the absolute value


def test_multiple_uses_gross_return():
    assert not failures("The best stock rose 11.4× in three years.".replace("three", "3"))


def test_indian_grouping_and_crore():
    assert not failures("Companies raised ₹1,25,000 crore.")
    assert not failures("Companies raised ₹1.25 lakh crore.")
    assert not failures("Companies raised ₹1.3 lakh crore.")   # 1.25 rounds to 1.3
    assert failures("Companies raised ₹1.4 lakh crore.") == ["1.4"]


def test_years_dates_and_names():
    assert not failures("Ritter (1991) studied IPOs; we use Nifty 500 and Smallcap 250 data for H1 since 2016.")
    assert failures("The boom of 2007 was different.") == ["2007"]
    assert failures("From 2016-07 on.") == ["2016-07"]


def test_non_citable_fact_is_not_allowed():
    assert failures("Prices climbed 358%.") == ["358"]


def test_number_words_are_checked():
    assert not failures("Newey-West with three lags.")
    assert failures("Newey-West with seven lags.") == ["seven"]
    assert not failures("About two-thirds of them fell.")   # fraction words go to the critic, not the gate


def test_approx_and_bounds():
    assert not failures("About 530 listings.")             # within 5%
    assert failures("About 600 listings.") == ["600"]
    assert not failures("More than 500 listings.")          # 529 > 500, within 10%
    assert failures("More than 100 listings.") == ["100"]   # true but loose: a bound must be tight
    assert not failures("A p-value has to be below 0.0167.")  # an exact context number under a bound word


def test_ranges_and_code_are_handled():
    rep = check("Shares rose 0.89–1.22 in t terms. `x = 99.9` and ```\ny = 123.4\n``` are code.", BUNDLE)
    assert rep["ok"], rep["failures"]
    assert [m.text for m in extract("Between 52% and 86% of listings")] == ["52", "86"]


def test_ordinals_and_tokens_are_skipped():
    assert [m.text for m in extract("The 3rd quarter, the 1st day, a 5Y window, T+1 settlement, FY26.")] == []
