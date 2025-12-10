# Changelog

All notable changes to Berserk Timer will be documented in this file.

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
- New threaded core with drift compensation and event bus for responsive controls.
- Witness Mode asks for activity notes and logs to `logs/witness_log_YYYY-MM-DD.txt`.
- Volume control with multiple alert sounds (`alert1-5.wav`), mute toggle, and on-the-fly restart/zero.
- Configurable presets via `config.json`; compact/`NO_COLOR` support for narrow or monochrome terminals.
- Graceful shutdown (Ctrl+C stops audio cleanly).

---

## [0.1.0-alpha] - 2024

- First prototype: basic countdown and logging.
