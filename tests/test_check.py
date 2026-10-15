"""End-to-end test of the free checks on a small fake study (no git freeze, no paid calls)."""

import json
import shutil
import textwrap

import pandas as pd
import pytest

from desk import check, data
from desk.config import STUDIES
from desk.results import Results
from desk.study import Study, prose_of

SLUG = "_pytest-study"

PLAN = textwrap.dedent("""\
    # test plan

    ## Sub-questions

    ### Q1. How often does it happen?

    - **Checks:** none (descriptive)

    ### Q2. Is waiting worth it?

    - **Checks:** robustness, era_split

    ## Amendments

    None yet.
    """)

ARTICLE = textwrap.dedent("""\
    ---
    title: "It happens 44% of the time"
    dek: "A test."
    date: 2026-10-15
    topic: ipo
    verdict: study
    finding: "It happened 44% of the time."
    signed_off: { by: null, on: null }
    ---

    import F from "./figures.json";

    <h2 id="q1">How often?</h2>

    It happened 44% of the time, across 120 listings.

    <Figure {...F.q1} />

    <h2 id="q2">Is waiting worth it?</h2>

    Waiting cost about 3.1 points a year.
    """)


@pytest.fixture
def study(tmp_path, monkeypatch):
    d = STUDIES / SLUG
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir()
    (d / "plan.md").write_text(PLAN)
    (d / "compute.py").write_text("# fake\n")
    store = tmp_path / "derived"
    store.mkdir()
    pd.DataFrame({"x": [1, 2]}).to_parquet(store / "t.parquet")
    monkeypatch.setattr(data, "PORTAL_DERIVED", store)
    monkeypatch.setattr(data, "_HASH_CACHE", tmp_path / "fp.json")
    yield d, store
    shutil.rmtree(d, ignore_errors=True)


def write_results(d, exploratory_headline=False):
    R = Results(d / "compute.py")
    data.load("portal:t", R)
    R.fact("q1_share", 0.44, "fraction", exploratory=exploratory_headline)
    R.fact("q1_n", 120, "count")
    R.fact("q2_cost", -0.031, "fraction")
    R.check("robustness", True, "start dates shifted", question="q2")
    R.check("era_split", True, "holds in both halves", question="q2")
    if exploratory_headline:
        R.tried_variant("by year")
    R.chart("q1", [{"a": 1}])
    R.write()


def write_article_and_figs(d):
    (d / "article.mdx").write_text(ARTICLE)
    from desk import figures
    figures.write(d / "figures.py", {"q1": {"title": "44% of the time", "read": "One bar per checkpoint.",
                                            "spec": {"kind": "hbars", "series": []}, "data": {"categories": [], "series": {}}}})


def status(items):
    return {i["check"]: i["status"] for i in items}


def test_plan_parsing(study):
    S = Study(SLUG)
    qs = S.questions()
    assert [q.id for q in qs] == ["q1", "q2"]
    assert qs[0].checks == [] and qs[1].checks == ["robustness", "era_split"]


def test_full_pass_without_paid_steps(study):
    d, _ = study
    write_results(d)
    write_article_and_figs(d)
    s = status(check.run(SLUG))
    for k in ("plan_shape", "results_fresh", "checks_passed", "declared_checks", "questions_answered", "figures_fresh",
              "numbers_traced", "headline_confirmatory", "style", "sections", "reader_copy_clean", "front_matter"):
        assert s[k] == "ok", (k, s)
    assert s["plan_frozen"] == s["recompute"] == s["review"] == s["human_read"] == "pending"


def test_untraced_number_fails(study):
    d, _ = study
    write_results(d)
    write_article_and_figs(d)
    (d / "article.mdx").write_text(ARTICLE.replace("across 120 listings", "across 125 listings"))
    assert status(check.run(SLUG))["numbers_traced"] == "fail"


def test_exploratory_fact_in_headline_fails(study):
    d, _ = study
    write_results(d, exploratory_headline=True)
    write_article_and_figs(d)
    s = status(check.run(SLUG))
    assert s["headline_confirmatory"] == "fail"
    assert s["numbers_traced"] == "ok"


def test_changed_input_and_code_make_results_stale(study):
    d, store = study
    write_results(d)
    write_article_and_figs(d)
    pd.DataFrame({"x": [1, 2, 3]}).to_parquet(store / "t.parquet")
    assert status(check.run(SLUG))["results_fresh"] == "fail"


def test_missing_declared_check_fails(study):
    d, _ = study
    write_results(d)
    res = json.loads((d / "results" / "results.json").read_text())
    del res["checks"]["q2:era_split"]
    (d / "results" / "results.json").write_text(json.dumps(res))
    assert status(check.run(SLUG))["declared_checks"] == "fail"


def test_internal_names_fail(study):
    d, _ = study
    write_results(d)
    write_article_and_figs(d)
    (d / "article.mdx").write_text(ARTICLE + "\nThe Data bank holds the prices.\n")
    assert status(check.run(SLUG))["reader_copy_clean"] == "fail"


def test_prose_of_strips_components():
    body = 'import F from "./f.json";\n\n<Figure {...F.q1} />\n\n<h2 id="q1">Title 2</h2>\n\nText.\n\n## References\n\nSmith 1991.'
    p = prose_of(body)
    assert "import" not in p and "Figure" not in p and "Title 2" in p and "1991" not in p
