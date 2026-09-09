# Changelog

All notable changes to Berserk Timer are documented here.

## Unreleased

### Fixed
- Launchers now forward user arguments unchanged and no longer inject a duration or witness mode.
- Windows launcher no longer depends on a machine-specific Python path.
- Windows shortcut helper now resolves paths from its own location, references the shipped `assets/icon.ico`, and creates a real `Berserk Timer.lnk` instead of a stale `.url` file.
- Repeated `Timer.start()` calls no longer create duplicate countdown threads.
- Timer duration accounting now uses a monotonic clock and is not affected by wall-clock jumps.
- Unknown CLI arguments are rejected instead of silently ignored.
- Explicit zero duration is validated as invalid instead of falling through to interactive mode.
- Windows `/h` and `/?` help aliases continue to work with strict argument parsing.
- Audio playback no longer depends on writable log files.
- Linux/macOS audio cleanup no longer uses system-wide `killall`, and Linux playback no longer changes the system master volume.
- Terminal cleanup resets the screen-manager singleton for clean repeated runs in the same process.
- Partial `config.json` files inherit required defaults without overwriting valid user values.
- Malformed JSON config files recover to canonical defaults instead of crashing startup.
- String booleans and individual preset values are normalized explicitly instead of relying on Python truthiness or unchecked values.
- Repository `config.json` now matches the application's canonical built-in defaults, so source and installed first-run behavior no longer drift.
- Runtime logs now use a user-scoped state directory instead of the current working directory.
- Non-finite timer durations such as `NaN` are rejected by the timer domain instead of entering an invalid countdown state.
- Runtime author/repository attribution points to `looksawful/berserk-timer`.

### Changed
- Audio playback and process ownership moved into `src/audio.py`; logging/persistence remains in `src/logger.py`.
- CLI audio controls now import the audio adapter directly; `src.logger` no longer exposes audio compatibility wrappers.
- Timer duration validation has one domain owner in `src.timer`; the CLI preserves its existing `(valid, message)` adapter contract.
- Packaging now uses `pyproject.toml` with an installable `berserk` console command.
- Runtime dependencies are separated from development/test dependencies.
- The ineffective virtual-environment bootstrap `setup.py` was removed.
- CI now includes Python 3.10/3.11/3.12 Linux tests, Windows Python 3.12 tests, install/entrypoint smoke tests, Ruff, MyPy and dependency auditing.
- GitHub Actions checkout/setup-python were updated to their current major versions.
- README and development documentation were reconciled with the implemented runtime and controls.

### Security / Safety
- `pip-audit` reports no known vulnerabilities in the current runtime dependency set at the time of this audit.
- Audio fallback processes are tracked and only processes started by Berserk Timer are terminated.

---

## [0.2.1-beta] - 2025-12-10

### Fixed
- `x` now opens the witness prompt instead of quitting; alert stops repeating after `k`.
- True silent start when using `--mute` or `volume: 0`.
- Logging no longer crashes in read-only environments (falls back to stderr).

### Changed
- Restart after completion now resets duration; `start()` works again post-finish.
- Volume range normalized to 0-10 with global mute override.
- Small UI polish (signature and log viewer ASCII art).

---

## [0.2.0-beta] - 2025-12-09

### Highlights
- Introduced the threaded `Timer` runtime used by the CLI.
- Witness Mode asks for activity notes and logs to `logs/witness_log_YYYY-MM-DD.txt`.
- Volume control with multiple alert sounds (`alert1-5.wav`), mute toggle, and on-the-fly restart/zero.
- Configurable presets via `config.json`; compact/`NO_COLOR` support for narrow or monochrome terminals.
- Graceful shutdown behavior for terminal/audio cleanup.

---

## [0.1.0-alpha] - 2024

- First prototype: basic countdown and logging.
