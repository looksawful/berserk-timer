# Timer core

Use this skill when changing timer duration, elapsed-time accounting, pause/resume, restart, zero, stop, worker lifecycle, or state transitions.

## Goal

Keep timing semantics deterministic and independent from terminal rendering, audio and filesystem behavior.

## Workflow

1. Read `src/timer.py` and the timer tests before editing.
2. State the behavior contract in a test first for bug fixes or semantic changes.
3. Use a monotonic clock for elapsed-time measurement. Wall-clock time is only for timestamps shown or written to logs.
4. Keep synchronization explicit. Shared timer state must be protected consistently; do not add sleeps as a substitute for synchronization.
5. Keep UI refresh frequency separate from timer accuracy.
6. Run `python -m pytest -q tests/test_timer.py tests/test_timer_drift.py tests/test_timer_runtime.py` and then the full suite.

## Invariants

- accepted duration is between the documented minimum and maximum;
- remaining time is never negative;
- pause freezes elapsed-time consumption;
- resume continues from the paused remainder;
- restart starts from the configured duration;
- zero terminates with zero remaining;
- stop leaves no live timer worker;
- repeated start/restart sequences do not leak threads;
- no timer-core import from CLI, Rich, pygame, terminal or screen modules.

## Avoid

- behavior changes hidden inside formatting/refactors;
- `time.time()` for elapsed duration;
- coupling alarm playback to the timer worker;
- assertions based on unrealistically exact scheduler timing.
