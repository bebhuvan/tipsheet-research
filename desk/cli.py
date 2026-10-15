"""The desk's command line: `uv run desk <command> <slug>`."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from .config import PORTAL_ROOT, ROOT, STUDIES, sha256_file, write_json
from .study import Study, git


def cmd_new(slug: str) -> int:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SystemExit("slug: lowercase words joined by hyphens")
    dest = STUDIES / slug
    if dest.exists():
        raise SystemExit(f"{dest} exists")
    shutil.copytree(STUDIES / "_template", dest)
    for p in dest.rglob("*"):
        if p.is_file():
            p.write_text(p.read_text().replace("{{slug}}", slug))
    print(f"created {dest}; start with guides/questions.md")
    return 0


def cmd_freeze(slug: str) -> int:
    S = Study(slug)
    rel = S.plan_path.relative_to(ROOT).as_posix()
    if git("status", "--porcelain", "--", rel).strip():
        raise SystemExit("plan.md has uncommitted changes: commit it on its own first")
    probs = S.plan_problems()
    if probs:
        raise SystemExit("plan problems:\n  " + "\n  ".join(probs))
    commit = git("log", "-1", "--format=%H", "--", rel).strip()
    if not commit:
        raise SystemExit("plan.md has never been committed")
    if S.freeze():
        raise SystemExit(f"already frozen at {S.freeze()['commit'][:7]}; later changes go under ## Amendments")
    write_json(S.freeze_path, {"commit": commit, "frozen_on": date.today().isoformat(), "plan_sha256": sha256_file(S.plan_path)})
    tag = f"{slug}/plan-frozen"
    git("tag", "-a", tag, commit, "-m", f"{slug}: plan frozen before any result was computed")
    print(f"{slug}: plan frozen at {commit[:7]}, tagged {tag}. Commit freeze.json, then push the branch and the tag now:\n"
          f"  git push origin HEAD {tag}\nGitHub's record of when the tag arrived is the public evidence that the plan came first.")
    return 0


def cmd_publish(slug: str, force_pending: bool = False, to: str | None = None, preview: bool = False) -> int:
    from . import check
    S = Study(slug)
    if not preview and check.main(slug, strict=not force_pending) != 0:
        raise SystemExit("desk check must pass first (use --preview to copy a draft into a preview checkout)")
    posts = (Path(to).expanduser() if to else PORTAL_ROOT) / "content" / "posts"   # --to: a portal worktree for previews
    if not posts.is_dir():
        raise SystemExit(f"portal posts folder not found: {posts}")
    text = S.article_path.read_text()
    text = re.sub(r'^import F from ".*?";$', f'import F from "./{slug}.figures.json";', text, flags=re.M)
    (posts / f"{slug}.mdx").write_text(text)
    shutil.copy(S.figures_path, posts / f"{slug}.figures.json")
    if not force_pending and not preview:
        tag = f"{slug}/published-{date.today().isoformat()}"
        git("tag", "-a", tag, "-m", f"{slug}: the version copied to the site")
        print(f"tagged {tag}; push it with the branch.")
    print(f"copied to {posts}/{slug}.mdx and {slug}.figures.json. Nothing was committed in the portal:"
          " preview it there, and commit only with the owner's go-ahead (pushing the portal's main publishes live).")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="desk")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("new", "freeze", "check", "recompute", "review", "audit", "report", "publish"):
        s = sub.add_parser(name)
        s.add_argument("slug")
        if name == "check":
            s.add_argument("--strict", action="store_true")
            s.add_argument("-v", "--verbose", action="store_true")
        if name == "publish":
            s.add_argument("--allow-pending", action="store_true", help="copy for a preview before sign-off")
            s.add_argument("--to", help="portal checkout to copy into (default PORTAL_ROOT), e.g. a preview worktree")
            s.add_argument("--preview", action="store_true", help="copy a draft without running desk check; never tags")
    a = p.parse_args(argv)
    if a.cmd == "new":
        return cmd_new(a.slug)
    if a.cmd == "freeze":
        return cmd_freeze(a.slug)
    if a.cmd == "check":
        from . import check
        return check.main(a.slug, a.strict, a.verbose)
    if a.cmd == "recompute":
        from . import recompute
        return recompute.main(a.slug)
    if a.cmd == "review":
        from . import review
        return review.main(a.slug)
    if a.cmd == "audit":
        from . import audit
        return audit.main(a.slug)
    if a.cmd == "report":
        from . import report
        return report.main(a.slug)
    if a.cmd == "publish":
        if a.preview and not a.to:
            raise SystemExit("--preview needs --to <a preview checkout>; never preview into the live portal")
        return cmd_publish(a.slug, a.allow_pending, a.to, a.preview)
    return 1


if __name__ == "__main__":
    sys.exit(main())
