# Berserk Timer agent guide

## Source of truth

- Work from `dev` unless an issue or PR explicitly says otherwise.
- Keep behavior changes, tooling changes, documentation changes, and asset changes in separate commits/PRs when practical.
- Do not change user-facing text, timing semantics, audio assets, or terminal behavior as part of cleanup unless the issue explicitly requires it.

## Required checks

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the behavioral baseline:

```bash
python -m compileall -q src
python -m pytest -q
```

Run advisory quality checks:

```bash
ruff check src tests
mypy src
pip-audit -r requirements.txt
```

Treat existing Ruff/MyPy findings as baseline debt. Do not combine broad auto-fixes with behavioral work.

## Architecture boundaries

The target dependency direction is:

1. timer/domain state
2. application orchestration
3. terminal/UI adapters
4. audio, filesystem, logging and platform infrastructure

The timer core must not depend on terminal rendering, keyboard input, sound playback, filesystem paths, or witness prompts. Platform-specific input/audio code should sit behind small adapters. `main` should assemble dependencies and run workflows, not contain core policy.

## Timer invariants

Any change touching duration or runtime state must preserve and test:

- duration validation and maximum limit;
- pause/resume does not consume paused time;
- restart restores the configured duration;
- zero ends the active timer deterministically;
- stop terminates the worker cleanly;
- remaining time never becomes negative;
- timing uses a monotonic source for elapsed-time semantics;
- UI refresh cadence must not define timer accuracy.

## CLI and platform contract

- Launchers must forward user arguments exactly once and must not inject an undocumented duration or mode.
- Never hard-code a machine-specific Python installation path.
- Windows is the primary interactive platform today; Linux CI is evidence for imports/core/tests, not proof that terminal interaction or audio works on Linux/macOS.
- Headless CI must set an audio fallback such as `SDL_AUDIODRIVER=dummy` when pygame is imported.
- Changes to keyboard handling, terminal alternate-buffer behavior, signal cleanup, or audio require explicit platform evidence.

## Documentation contract

README, help output, launchers, config defaults and actual runtime behavior must agree. Do not document engines, commands, files or install flows that do not exist in the repository.

## Review order

For a non-trivial change, review in this order:

1. issue/behavior contract;
2. tests that prove the current and desired behavior;
3. smallest implementation change;
4. Linux CI baseline;
5. Windows/manual evidence when platform behavior is involved;
6. docs and changelog sync.
