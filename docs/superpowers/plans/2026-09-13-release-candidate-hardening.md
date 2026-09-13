# Berserk Timer 0.3.0-beta Release Candidate Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a release-ready Berserk Timer 0.3.0-beta candidate that preserves the current ASCII UI, WAV alerts and command behavior while closing the remaining interrupt-safety and release-verification gaps.

**Architecture:** Keep the existing dependency direction `timer/domain -> session/application -> CLI/audio/log/config adapters`. Add one small input adapter for EOF/KeyboardInterrupt normalization, keep command semantics in the existing CLI layer for this release, and add release contracts around assets/package installation instead of rewriting working audio/UI code.

**Tech Stack:** Python 3.10-3.12, pytest, Rich, pygame, setuptools/pyproject, GitHub Actions on Ubuntu and Windows.

**Spec:** `docs/ARCHITECTURE.md`, issues #6 and #8, and the current `Unreleased` section in `CHANGELOG.md`.

## Global Constraints

- Preserve all current CLI text, shortcuts, timing behavior and ASCII/audio assets unless a failing regression test proves a required fix.
- Do not modify the WAV files or ASCII artwork during release hardening.
- Python support remains 3.10, 3.11 and 3.12.
- Windows remains the primary interactive platform; Linux core behavior remains continuously tested.
- Every runtime bugfix follows RED -> GREEN -> full-matrix verification.
- Release completion requires Linux 3.10/3.11/3.12 tests, Windows 3.12 tests, Ruff, MyPy, pip-audit, package install/import/help smoke and installed audio-asset smoke.

---

### Task 1: Interrupt-safe input adapter

**Files:**
- Create: `src/input_utils.py`
- Create: `tests/test_input_utils.py`

**Interfaces:**
- Produces: `read_input(prompt: str = "") -> str | None`
- Contract: returns the exact string from `input()`; returns `None` for `EOFError` or `KeyboardInterrupt`.

- [ ] **Step 1: Write the failing tests**

```python
import src.input_utils as input_utils


def test_read_input_returns_user_text(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt="": "hello")
    assert input_utils.read_input("prompt") == "hello"


def test_read_input_returns_none_on_eof(monkeypatch):
    def raise_eof(_prompt=""):
        raise EOFError
    monkeypatch.setattr("builtins.input", raise_eof)
    assert input_utils.read_input("prompt") is None


def test_read_input_returns_none_on_keyboard_interrupt(monkeypatch):
    def raise_interrupt(_prompt=""):
        raise KeyboardInterrupt
    monkeypatch.setattr("builtins.input", raise_interrupt)
    assert input_utils.read_input("prompt") is None
```

- [ ] **Step 2: Run the focused tests and confirm RED**

Run: `python -m pytest -q tests/test_input_utils.py`
Expected: import failure because `src.input_utils` does not exist.

- [ ] **Step 3: Implement the minimum adapter**

```python
def read_input(prompt: str = "") -> str | None:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return None
```

- [ ] **Step 4: Run focused tests and confirm GREEN**

Run: `python -m pytest -q tests/test_input_utils.py`
Expected: all tests pass.

### Task 2: Apply interrupt policy without changing normal CLI behavior

**Files:**
- Modify: `src/main.py`
- Modify: `src/session.py`
- Modify: `src/cli.py`
- Modify: `tests/test_main.py`
- Modify: `tests/test_session.py`
- Create: `tests/test_interrupt_paths.py`

**Interfaces:**
- Consumes: `read_input(prompt) -> str | None`
- Normal typed input remains byte-for-byte equivalent after `.strip()`/`.lower()` at each existing call site.

- [ ] **Step 1: Add failing behavior tests**

Test these policies explicitly:
- initial duration prompt interrupted -> `main()` returns cleanly without entering the timer loop;
- quit confirmation interrupted -> quit is cancelled and timer is not stopped;
- update-duration and goal prompts interrupted -> operation is cancelled, timer state unchanged;
- witness skip confirmation interrupted -> witness returns `"Witness skipped."` and stops alert cleanup;
- post-completion restart prompt interrupted -> session loop exits instead of raising;
- restart duration prompt interrupted -> session loop exits instead of raising.

- [ ] **Step 2: Confirm RED against the current direct `input()` call sites**

Run: `python -m pytest -q tests/test_interrupt_paths.py tests/test_main.py tests/test_session.py`
Expected: focused failures from unhandled `EOFError`/`KeyboardInterrupt` paths.

- [ ] **Step 3: Replace direct calls with `read_input()` one call site at a time**

Policies:
- `None` at application/session boundary means cancel/exit the current interactive flow cleanly;
- `None` inside a command confirmation means cancel that command and keep the timer running;
- `None` at witness input/confirmation means skip witness and stop alert cleanup;
- an actual empty string keeps the existing meaning, including default-duration confirmation and explicit goal clearing.

- [ ] **Step 4: Re-run focused tests, then full suite**

Run: `python -m pytest -q`
Expected: zero failures.

### Task 3: Freeze ASCII and command-surface release contracts

**Files:**
- Create: `tests/test_release_ui_contract.py`

**Interfaces:**
- Reads existing `src.ascii_art` constants and `src.cli`/`src.main` sources only.
- Does not modify any user-visible strings or artwork.

- [ ] **Step 1: Add characterization tests**

Verify all six artworks are present and non-empty: `ASCII_LOGO`, `ASCII_SETTINGS`, `ASCII_HELP`, `ASCII_BYE`, `ASCII_WITNESS_LOG`, `ASCII_FINISHED`.
Verify `show_help()` still prints `ASCII_LOGO`.
Verify timer command map still registers `p q x r v d u g m s k h` and raw keyboard input still delegates to `dispatch_command`.

- [ ] **Step 2: Run the characterization tests**

Run: `python -m pytest -q tests/test_release_ui_contract.py`
Expected: pass on the current intended UI contract.

### Task 4: Freeze source and installed audio contracts

**Files:**
- Create: `tests/test_release_audio_contract.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Uses `src.audio.get_available_sounds()`, `get_sound_path()` and `get_sound_duration()`.
- Expected shipped alerts: `alert1.wav` through `alert5.wav`.

- [ ] **Step 1: Add source-tree audio asset tests**

```python
EXPECTED = [f"alert{i}.wav" for i in range(1, 6)]
assert audio.get_available_sounds() == EXPECTED
for name in EXPECTED:
    path = Path(audio.get_sound_path(name))
    assert path.is_file()
    assert audio.get_sound_duration(str(path)) > 0
```

Also retain ownership safety checks: no system `killall`, no `amixer`, newer playback stops the previously owned playback.

- [ ] **Step 2: Extend package smoke for installed assets**

After `python -m pip install .`, run a Python snippet that asserts all five installed WAV files are discoverable, exist, and have positive WAV duration.

- [ ] **Step 3: Run full CI matrix**

Expected: Linux 3.10/3.11/3.12, Windows 3.12, static audit and package smoke all pass.

### Task 5: Release metadata and documentation

**Files:**
- Modify: `src/version.py`
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `.agents/skills/cli-platform/SKILL.md`
- Modify: `.agents/skills/release-quality/SKILL.md`

**Interfaces:**
- Public version string: `0.3.0-beta`
- PEP 440 package version: `0.3.0b0`

- [ ] **Step 1: Add a version-consistency test before changing metadata**

The test must require the public version, package version and README heading to describe the same release.

- [ ] **Step 2: Confirm RED on existing `0.2.1-beta`/Unreleased state when targeting 0.3.0-beta**

- [ ] **Step 3: Update version metadata and move completed changelog entries into `[0.3.0-beta] - 2026-09-13`**

Keep a fresh empty `Unreleased` section above the release.

- [ ] **Step 4: Reconcile stale agent docs**

Document that `pip install .`/`berserk` packaging exists and Ruff/MyPy are enforced CI gates, not advisory debt.

### Task 6: Consolidation, merge and release gate

**Files:**
- No runtime changes unless a release gate exposes a reproducible defect.

- [ ] **Step 1: Open the release-candidate PR directly against `dev`**

It must contain the full #13 -> #16 -> #17 -> #18 stack plus Tasks 1-5, so the merge target is unambiguous.

- [ ] **Step 2: Run fresh PR CI against `dev`**

Do not rely on historical stacked-PR runs.

- [ ] **Step 3: Compare release candidate to `dev`**

Verify there are no WAV or ASCII artwork modifications and no accidental unrelated files.

- [ ] **Step 4: Merge only after fresh full-matrix success**

Close/supersede redundant stacked PRs #13-#18 after the consolidated merge.

- [ ] **Step 5: Merge or retarget runtime-neutral PR #19 separately**

Do not let agent-skill documentation obscure runtime release evidence.

- [ ] **Step 6: Run CI on merged `dev` again**

The post-merge SHA must pass the same matrix.

- [ ] **Step 7: Tag and publish `v0.3.0-beta`**

Release notes must summarize runtime correctness, config/log storage, CLI architecture, shortcut repair, interrupt safety and verification. Do not publish before the post-merge gate is green.
