# Development and verification

## Environment

Recommended supported development baseline for the current repository audit is Python 3.10–3.12.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# POSIX
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` currently includes the existing runtime/test requirements and adds Ruff, MyPy and pip-audit. A later packaging issue should separate true runtime dependencies from test/dev dependencies cleanly.

## Behavioral checks

```bash
python -m compileall -q src
python -m pytest -q
```

The audit branch established a Linux CI baseline on Python 3.10, 3.11 and 3.12. At the first run all three jobs passed, with 21 tests passing on Python 3.12.

For pygame in headless Linux CI:

```bash
export SDL_AUDIODRIVER=dummy
export PYGAME_HIDE_SUPPORT_PROMPT=1
```

This proves source importability and the existing automated behavior on the CI runner. It does not prove interactive terminal/audio behavior on Windows, Linux desktop or macOS.

## Static-quality baseline

```bash
ruff check src tests
mypy src
pip-audit -r requirements.txt
```

These checks begin as advisory evidence so historical debt can be inventoried without blocking the behavioral test matrix. New changes should avoid adding new findings.

The first Ruff baseline found 64 findings, with 37 reported as automatically fixable. They include import ordering/modernization and line-length debt, but also concrete unused imports/variables. Do not run a repository-wide autofix inside an unrelated behavioral PR.

## Focused timer tests

```bash
python -m pytest -q \
  tests/test_timer.py \
  tests/test_timer_drift.py \
  tests/test_timer_runtime.py
```

## Manual smoke checks

For a release or platform-affecting change, record at least:

```bash
python -m src.main --help
python -m src.main 2 --seconds --mute
```

Then verify platform-specific key handling, alternate-screen cleanup and real audio on the claimed primary platform. The current project states Windows as primary, so Windows evidence matters before making strong compatibility claims.

## Branch/PR discipline

- Start from fresh `dev`.
- One behavior contract per issue when practical.
- Add RED evidence before a correctness refactor.
- Keep docs/tooling-only work behavior-neutral.
- Avoid broad formatter changes in bug fixes.
- Update README/help/changelog only after the implementation contract is proven.

## Agent files

`AGENTS.md` is the repository-wide contract. More focused instructions live under:

- `.agents/skills/timer-core/SKILL.md`
- `.agents/skills/cli-platform/SKILL.md`
- `.agents/skills/release-quality/SKILL.md`

Agents should load the narrow skill that matches the task rather than treating every change as a full architecture rewrite.
