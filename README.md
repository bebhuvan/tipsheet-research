# tipsheet research

Finance research with academic rigour, written for people who manage their own money. Studies are published on tipsheet.markets under /research/.

- How a study is done: `CLAUDE.md` (also `AGENTS.md`)
- Why it's built this way: `docs/DESIGN.md`
- The guides for each step: `guides/`

Setup:

```
cp .env.example .env     # fill in paths and keys; chmod 600 .env
uv sync
uv run pytest
```
