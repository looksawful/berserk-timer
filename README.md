# Berserk Timer 0.2.1-beta

```text
███   ▄███▄   █▄▄▄▄   ▄▄▄▄▄   ▄███▄   █▄▄▄▄ █  █▀
█  █  █▀   ▀  █  ▄▀  █     ▀▄ █▀   ▀  █  ▄▀ █▄█
█ ▀ ▄ ██▄▄    █▀▀▌ ▄  ▀▀▀▀▄   ██▄▄    █▀▀▌  █▀▄
█  ▄▀ █▄   ▄▀ █  █  ▀▄▄▄▄▀    █▄   ▄▀ █  █  █  █
███   ▀███▀      █             ▀███▀     █     █
                ▀                       ▀     ▀
             █▄
           ▄     █▀▄▀█
       ▄▄▄▀▀ ▄█  █ █ █  ▄███▄   █▄▄▄▄
    ▀▀▀ █    ██  █ ▀ █  █▀   ▀  █  ▄▀
        █    ██  █   █  ██▄▄    █▀▀█▌
       █     ▐█      █  █▄   ▄▀ █   █
      ▀       ▐     ▀   ▀███▀      █
```

Berserk Timer is a small Python CLI timer with flexible duration input, presets, interactive controls, audio alerts, goals and optional witness logging after a session.

## Status

The project is beta software. Windows is the primary platform and has a dedicated CI lane. The portable core and test suite are also exercised on Linux with Python 3.10, 3.11 and 3.12. Linux and macOS audio/terminal behavior still depends on the host terminal and available audio backend, so platform-specific interactive behavior should be treated more cautiously than the core timer tests.

The active timer engine is `src.timer.Timer`. Duration accounting uses a monotonic clock so system clock changes do not alter elapsed timer time.

## Installation

Python 3.10 or newer is required.

Install from a clone:

```bash
git clone https://github.com/looksawful/berserk-timer.git
cd berserk-timer
python -m pip install .
```

This installs the global command:

```bash
berserk --help
berserk 25
berserk -s -w
```

For development:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
ruff check src tests
mypy src
pip-audit -r requirements.txt
```

You can also run directly from the repository:

```bash
python -m src.main 25
```

Windows users may use `brsrk.bat`; Linux/macOS users may use `./brsrk.sh`. Both wrappers forward the supplied CLI arguments unchanged.

## Duration and presets

A positional duration is interpreted as minutes by default:

```bash
berserk 10
berserk 1.5
berserk 90 --seconds
```

Default presets are:

- `-x`: 5 minutes
- `-s`: 10 minutes
- `-m`: 15 minutes
- `-l`: 20 minutes
- `-X`: 25 minutes
- `-t`: 1 minute test preset

The maximum duration is defined centrally by the application and validated both at startup and when changing a running timer.

## Options

```text
-h, --help, /h, /?   Show help
-x                    Extra-small preset
-s                    Small preset
-m                    Medium preset
-l                    Large preset
-X                    Extra-large preset
-t                    Test preset
-w                    Enable witness mode
-c MESSAGE            Custom advice message
--sound FILE          Select an alert WAV file
--seconds             Interpret positional duration as seconds
--mute                Start silent
--debug               Disable alternate-screen clearing for debugging
```

Unknown arguments are rejected instead of being silently ignored.

## Controls while running

- `p`: pause/resume
- `q`: quit with confirmation
- `x`: zero the timer
- `r`: restart
- `v`: view today's witness log
- `d`: delete today's witness log
- `u`: change duration
- `g`: set or clear the goal
- `m`: toggle silent mode
- `s`: open audio settings
- `k`: stop the currently playing alert
- `h`: show in-app help

## Witness logging

When witness mode is enabled, the timer asks what was accomplished after the session. The default safe word is `skip`.

Logs are written to:

```text
logs/berserk.log
logs/witness_log_YYYY-MM-DD.txt
```

If the log directory is not writable, regular log messages fall back to stderr. Audio playback is independent from log-file availability.

## Audio

Runtime audio is isolated in `src/audio.py`. `pygame` is the primary playback backend and uses per-application volume from 0 to 10. Native platform players are fallbacks where appropriate.

Berserk Timer only terminates audio processes it started itself. It does not use system-wide `killall` and does not change the operating system's master volume.

Available WAV files are discovered from the repository assets directory when running from source and from the installed package assets directory after `pip install .`.

## Configuration

`config.json` is loaded with required defaults filled in when older or partial configuration files omit fields. User-provided values are preserved where valid.

Current default shape:

```json
{
  "messages": [
    "Drink water",
    "Do push-ups",
    "Take a short walk"
  ],
  "presets": {
    "xs": 5,
    "s": 10,
    "m": 15,
    "l": 20,
    "xl": 25,
    "test": 1
  },
  "witness_mode": true,
  "safe_word": "skip",
  "sound_file": "alert1.wav",
  "volume": 5
}
```

`volume` is clamped to the supported 0–10 range. Empty messages are removed, and invalid/missing required fields fall back to application defaults.

## Architecture

The main runtime boundaries are:

```text
src.timer          timer state and duration semantics
src.main           application/session orchestration
src.cli            terminal interaction and commands
src.audio          audio playback and owned process lifecycle
src.logger         system/witness persistence
src.config_manager configuration loading and normalization
src.screen_manager terminal screen lifecycle
```

See `docs/ARCHITECTURE.md` and `docs/DEVELOPMENT.md` for the detailed dependency map, verification workflow and agent rules.

## Verification

CI currently checks:

- pytest on Linux with Python 3.10, 3.11 and 3.12;
- pytest on Windows with Python 3.12;
- source compilation;
- package installation and the `berserk` console entry point;
- Ruff correctness checks;
- MyPy;
- `pip-audit` against runtime dependencies.

Regression tests cover launcher argument forwarding, duplicate timer threads, monotonic duration accounting, strict argument parsing, explicit zero-duration validation, partial configuration repair, audio ownership and terminal cleanup.

## License

Berserk Timer is provided under the repository's personal/non-commercial license. Audio assets remain subject to the terms in `LICENSE`, and third-party dependencies retain their own licenses.

See [LICENSE](LICENSE) for the complete terms.
