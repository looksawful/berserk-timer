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
                |
                +----> src.commands
                |      key-independent command dispatch
                |
                +----> src.input_utils
                       EOF/Ctrl+C-safe text input

src.main ----------> src.input_utils
src.session -------> src.input_utils
src.logger          system + witness persistence
src.config_manager  user-scoped configuration + migration
src.screen_manager  terminal screen lifecycle
```

## Dependency contracts

### `src.timer`

Owns duration validation and timer state. Elapsed duration uses `time.monotonic()`, so wall-clock corrections cannot change countdown semantics. The timer does not import Rich, pygame, terminal input or configuration code.

Repeated `start()` calls while a timer is already running are idempotent and cannot create competing countdown threads. Duration validation has one domain owner and rejects non-finite values such as `NaN`.

### `src.session`

Owns the application workflow after initial input: creating a timer, running the CLI loop, handling completion, witness collection, restart behavior and repeating alert escalation. This keeps `src.main` from being both the entry point and the complete application service.

Interactive restart/duration/goal prompts use the shared input adapter so EOF and Ctrl+C exit the active session flow cleanly.

### `src.cli`

Owns terminal rendering, platform keyboard polling and interactive command handlers. Platform keyboard paths remain adapter-level concerns here. Raw key polling does not own command lookup: printable command keys are delegated to `src.commands.dispatch_command`.

Text prompts use `src.input_utils.read_input` rather than calling the builtin `input()` directly. This keeps EOF/Ctrl+C behavior explicit and testable while preserving the existing meaning of normal input and empty strings.

CLI code may call persistence and audio APIs, but timer-domain behavior stays in `Timer`.

### `src.commands`

Owns raw-key-independent command dispatch. It receives one key plus a handler mapping, normalizes the key case-insensitively and invokes at most one matching handler. It has no Rich, terminal, timer, audio or filesystem dependency.

This boundary lets the command surface be tested without emulating `msvcrt`, termios or a physical terminal.

### `src.input_utils`

Owns the small text-input interruption contract. `read_input(prompt)` returns the exact string returned by `input()` and returns `None` for `EOFError` or `KeyboardInterrupt`.

Call sites decide what `None` means for their flow: cancel a command, skip witness logging, stop a restart sequence or exit initial interactive setup. An actual empty string remains distinct from interruption.

### `src.audio`

Owns playback state and platform audio backends. `pygame` is the primary backend. Native `aplay`/`afplay` are fallbacks and are tracked as concrete child processes.

Audio invariants:

- no system-wide `killall`;
- no mutation of system master volume;
- only a process started by Berserk Timer may be terminated by Berserk Timer;
- starting a new playback stops the previous playback first;
- stale playback threads cannot mark a newer playback as finished;
- file-logging availability does not affect audio availability;
- global mute blocks new playback;
- the release package ships and discovers `alert1.wav` through `alert5.wav`.

### `src.logger`

Owns application logging and witness-log persistence only. Audio playback is not exposed through this module; runtime code imports audio behavior from `src.audio` directly.

When the log directory is unavailable, regular log messages fall back to stderr. Runtime logs use a user-scoped state location rather than the caller's current working directory.

### `src.config_manager`

Owns default configuration, validation/normalization and config location.

Default user config locations:

- Windows: `%APPDATA%/Berserk Timer/config.json`;
- macOS: `~/Library/Application Support/Berserk Timer/config.json`;
- Linux/Unix: `$XDG_CONFIG_HOME/berserk-timer/config.json` or `~/.config/berserk-timer/config.json`.

On the first user-scoped run, a legacy source-tree `config.json` is copied to the user location if present. Explicit `load_config(path)` calls continue to use exactly the supplied path, which keeps tests and tools deterministic.

Malformed or partial configuration is normalized against canonical defaults instead of crashing startup. String booleans and preset values are parsed explicitly.

### `src.screen_manager`

Owns alternate-screen entry/exit and terminal cleanup. Cleanup resets the singleton so another application run in the same Python process receives a fresh manager.

## Packaging

Packaging is defined in `pyproject.toml` using setuptools. Runtime dependencies are separate from development dependencies. `python -m pip install .` installs the `berserk` console command and application assets.

The package smoke gate changes to a directory outside the source checkout before validating installed audio assets. This prevents repository files from masking missing package data.

The old `setup.py` bootstrap was removed because running an activation script in a child process cannot activate the caller's shell.

## Verification boundaries

CI provides independent evidence for:

- Linux tests on Python 3.10, 3.11 and 3.12;
- Windows tests on Python 3.12;
- source compilation;
- package installation, import and `berserk --help` entrypoint smoke;
- all five installed WAV alerts outside the source checkout, including positive parsed WAV duration;
- ASCII artwork and command-key release contracts;
- EOF/Ctrl+C behavior across startup, session and witness flows;
- Ruff correctness checks;
- MyPy type checks;
- `pip-audit` against runtime dependencies.

Interactive behavior that depends on a particular terminal emulator, focus model, sound driver or physical audio device still needs real-platform evidence. A green headless CI run proves the tested software contracts and packaged audio integrity; it is not claimed as proof that every speaker/driver/terminal combination produces audible output.

## Change discipline

Behavior-sensitive work should keep the RED/GREEN sequence:

1. reproduce the defect or define the contract in a focused test;
2. make the smallest root-cause fix;
3. run the focused test and full suite;
4. run static and package checks;
5. update documentation when a public contract changed.

Avoid broad formatting or modernization changes in the same commit as timer, terminal or audio behavior changes.
