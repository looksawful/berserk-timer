# Development and verification

## Environment

Supported development and CI baseline: Python 3.10, 3.11 and 3.12.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# POSIX
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Runtime dependencies live in `requirements.txt` and package metadata in `pyproject.toml`. Test, lint, type-check and audit tools live in `requirements-dev.txt`.

## Behavioral checks

```bash
python -m compileall -q src
python -m pytest -q
```

CI runs the full test suite on Linux with Python 3.10, 3.11 and 3.12 and on Windows with Python 3.12.

For pygame in headless CI:

```bash
export SDL_AUDIODRIVER=dummy
export PYGAME_HIDE_SUPPORT_PROMPT=1
```

These runs prove the automated software contracts on the CI runners. They do not claim that every physical audio device, sound driver or terminal emulator has been exercised.

## Static and dependency gates

```bash
ruff check src tests
mypy src
pip-audit -r requirements.txt
```

All three are enforced release gates. A release candidate is not clean while Ruff or MyPy reports findings or while the runtime dependency audit reports an unresolved known vulnerability.

Historical audit counts from the initial repository baseline are not the current quality state and should not be used as release evidence.

## Focused timer tests

```bash
python -m pytest -q \
  tests/test_timer.py \
  tests/test_timer_drift.py \
  tests/test_timer_runtime.py
```

Timer changes must preserve monotonic duration accounting, idempotent `start()` behavior and centralized duration validation.

## Interactive input checks

Interactive runtime modules use `src.input_utils.read_input` rather than calling builtin `input()` directly. EOF or Ctrl+C is represented as `None`, and each call site applies an explicit policy such as cancelling a command, skipping witness input or exiting a restart flow.

Focused regression coverage lives in:

```bash
python -m pytest -q \
  tests/test_input_utils.py \
  tests/test_interrupt_paths.py
```

An actual empty string remains a normal user response and must not be conflated with interruption.

## Audio and release UI checks

The release ships `alert1.wav` through `alert5.wav`. Source-tree tests verify that all five are discoverable and parse as WAV files with positive duration. Package smoke tests install the project, change outside the repository checkout, then repeat the asset checks against the installed package data.

Release characterization tests also protect the ASCII artwork and the timer command-key surface.

```bash
python -m pytest -q \
  tests/test_audio_ownership.py \
  tests/test_release_audio_contract.py \
  tests/test_release_ui_contract.py
```

Do not modify shipped WAV bytes or ASCII artwork as part of unrelated release hardening.

## Package smoke checks

```bash
python -m pip install .
berserk --help
```

When verifying installed package data, run the validation from a directory outside the repository so local `assets/` files cannot hide a packaging error.

`pyproject.toml` is the packaging source of truth. The installed command is `berserk`; `python -m src.main` remains the supported direct source invocation.

## Manual smoke checks

For a release or platform-affecting change, record at least:

```bash
python -m src.main --help
python -m src.main 2 --seconds --mute
```

Then verify platform-specific key handling, alternate-screen cleanup and real audio on the claimed primary platform when such hardware evidence is available. Windows is the primary platform, so the dedicated Windows CI lane is mandatory before release.

## Release gate

Before publishing a release:

1. confirm runtime version, `pyproject.toml`, README and CHANGELOG agree;
2. run the full Linux/Windows CI matrix on the exact release-candidate SHA;
3. compare the release candidate against `dev` and verify no accidental WAV or ASCII-art modifications;
4. merge to `dev` only after that gate is green;
5. run the same CI matrix again on the merged `dev` SHA;
6. create the tag/release only after post-merge CI succeeds.

Historical green runs from an earlier branch SHA are useful evidence but do not replace the exact release-candidate and post-merge gates.

## Branch/PR discipline

- Start from fresh `dev` for independent work, or explicitly document a stacked base.
- One behavior contract per issue when practical.
- Add RED evidence before a correctness refactor.
- Keep docs/tooling-only work behavior-neutral.
- Avoid broad formatter changes in bug fixes.
- Update README/help/changelog only after the implementation contract is proven.
- Prefer a consolidated release-candidate PR directly against `dev` when several verified stacked PRs need to ship together.

## Agent files

`AGENTS.md` is the repository-wide contract. More focused instructions live under:

- `.agents/skills/timer-core/SKILL.md`
- `.agents/skills/cli-platform/SKILL.md`
- `.agents/skills/release-quality/SKILL.md`

Agents should load the narrow skill that matches the task rather than treating every change as a full architecture rewrite.
