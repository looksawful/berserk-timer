# Changelog

All notable changes to Berserk Timer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Export witness logs to CSV/JSON
- Configurable audio files
- Improved GUI interface

## [0.1.4-beta] - 2025-11-23

### Added
- ASCII logo display on startup
- Interactive startup mode: asks for duration and goal before timer starts
- `is_paused()` method in Timer class

### Changed
- **Simplified hotkeys:** Combined `p` (pause) and `r` (resume) into single `p` key for toggle pause/resume
- Hotkey descriptions updated: `z` now correctly described as "zero timer", `n` as "restart", `u` as "update duration"
- Logo and welcome message now shown before any timer initialization
- Interactive mode improved with better prompts and default values

### Removed
- Separate `r` hotkey for resume (merged with `p`)

### Fixed
- Duplicate `*.pyd` entry in .gitignore removed
- Cleaner .gitignore with better organization

## [0.1.3-beta] - 2025-11-23

### Added
- `safe_word` configuration option with default value "skip"
- Message sanitization on config load (removes empty strings)
- Test coverage for config validation and sanitization
- `config.example.json` as template for user configuration

### Changed
- Test preset duration changed from 0.1 minutes (6 seconds) to 1 minute
- Improved config loading with fallback for missing safe_word

### Fixed
- "Timer ended" log now only appears when timer completes naturally
- Empty messages no longer saved to witness logs
- Config validation ensures safe_word is always present

### Modified Files
- `src/config_manager.py` - Config defaults and validation
- `src/main.py` - Timer end logging fix
- `tests/test_config.py` - New test cases
- `.gitignore` - Extended to cover more Python artifacts

## [0.1.2-beta] - 2025-02-XX

### Added
- Witness mode functionality
- Activity logging system
- CLI interactive commands during timer execution

### Changed
- Improved Rich CLI interface with better visual feedback

## [0.1.1-beta] - 2025-01-XX

### Added
- Basic timer functionality
- Preset durations (xs, s, m, l, xl)
- Sound notifications using Pygame
- Configuration file support

### Fixed
- Various CLI display issues
- Timer accuracy improvements

## [0.1.0-alpha] - 2024-XX-XX

### Added
- Initial release
- Basic CLI timer
- Duration input in minutes
- Simple logging

---

## Legend

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security fixes
