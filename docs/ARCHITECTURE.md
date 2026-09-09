# Berserk Timer architecture

## Runtime map

The canonical package entry point is `src.main:main`, exposed as the installed `berserk` command. Repository launchers (`brsrk.bat`, `brsrk.sh`) only select a Python interpreter and forward user arguments unchanged.

```text
brsrk.bat / brsrk.sh / berserk
                |
                v
            src.main
      startup / argument parsing
      initial duration + goal input
      dependency composition
                |
                v
           src.session
      timer-session orchestration
      restart / witness / alarms
        /       |        \
       v        v         v
 src.timer   src.cli   src.audio
     |          |         |
     |          |         +-- pygame / owned native fallback process
     |          +------------ Rich / keyboard / screen interaction
     +----------------------- monotonic timer state + duration rules

src.logger          system + witness persistence
src.config_manager  user-scoped configuration + migration
src.screen_manager  terminal screen lifecycle
```

## Dependency contracts

### `src.timer`

Owns the single authoritative duration validation function and timer state. All startup, restart and in-session duration changes use the same domain rules. Durations must be finite, positive, at least one second and no longer than `MAX_TIMER_SECONDS`.

Elapsed duration uses `time.monotonic()`, so wall-clock corrections cannot change countdown semantics. The timer does not import Rich, pygame, terminal input or configuration code.

Repeated `start()` calls while a timer is already running are idempotent and cannot create competing countdown threads.

### `src.session`

Owns the application workflow after initial input: creating a timer, running the CLI loop, handling completion, witness collection, restart behavior and repeating alert escalation. This keeps `src.main` from being both the entry point and the complete application service.

### `src.cli`

Owns terminal rendering, keyboard input and interactive commands. Platform keyboard paths remain adapter-level concerns here. CLI code calls `src.audio` directly for playback actions and `src.logger` only for persistence actions. Timer-domain behavior, including duration validation, stays in `src.timer`/`Timer`.

### `src.audio`

Owns playback state and platform audio backends. `pygame` is the primary backend. Native `aplay`/`afplay` are fallbacks and are tracked as concrete child processes.

Audio invariants:

- no system-wide `killall`;
- no mutation of system master volume;
- only a process started by Berserk Timer may be terminated by Berserk Timer;
- starting a new playback stops the previous playback first;
- stale playback threads cannot mark a newer playback as finished;
- file-logging availability does not affect audio availability.

### `src.logger`

Owns application logging and witness-log persistence only. It does not expose or proxy audio APIs. When the log directory is unavailable it falls back to stderr.

### `src.config_manager`

Owns default configuration, validation/normalization and config location.

Default user config locations:

- Windows: `%APPDATA%/Berserk Timer/config.json`;
- macOS: `~/Library/Application Support/Berserk Timer/config.json`;
- Linux/Unix: `$XDG_CONFIG_HOME/berserk-timer/config.json` or `~/.config/berserk-timer/config.json`.

On the first user-scoped run, a legacy source-tree `config.json` is copied to the user location if present. Explicit `load_config(path)` calls continue to use exactly the supplied path, which keeps tests and tools deterministic.

### `src.screen_manager`

Owns alternate-screen entry/exit and terminal cleanup. Cleanup resets the singleton so another application run in the same Python process receives a fresh manager.

## Packaging

Packaging is defined in `pyproject.toml` using setuptools. Runtime dependencies are separate from development dependencies. `python -m pip install .` installs the `berserk` console command and application assets.

The old `setup.py` bootstrap was removed because running an activation script in a child process cannot activate the caller's shell.

## Verification boundaries

CI provides independent evidence for:

- Linux tests on Python 3.10, 3.11 and 3.12;
- Windows tests on Python 3.12;
- source compilation;
- package installation, import and `berserk --help` entrypoint smoke;
- Ruff correctness checks;
- MyPy type checks;
- `pip-audit` against runtime dependencies.

Interactive behavior that depends on a particular terminal emulator, focus model or physical audio device still needs manual platform evidence. A green headless CI run is not claimed as proof of every terminal/audio-device combination.

## Change discipline

Behavior-sensitive work should keep the RED/GREEN sequence:

1. reproduce the defect or define the contract in a focused test;
2. make the smallest root-cause fix;
3. run the focused test and full suite;
4. run static and package checks;
5. update documentation when a public contract changed.

Avoid broad formatting or modernization changes in the same commit as timer, terminal or audio behavior changes.
