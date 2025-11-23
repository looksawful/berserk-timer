# Berserk Timer 0.1.3-beta

```plaintext
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

> **Status:** 🔧 Active Development | **Priority:** 🔥 Critical
> **Recent Updates (Nov 23, 2025):**
> - ✅ Fixed: Added `safe_word` to config defaults
> - ✅ Fixed: Test preset changed from 0.1 to 1 minute
> - ✅ Fixed: Message sanitization (removes empty strings)
> - ✅ Fixed: Premature "Timer ended" logging
> - 🚧 In Progress: Mute/Silent mode CLI flags

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Quick Install (Windows)](#quick-install-windows)
  - [Quick Install (Linux/MacOS)](#quick-install-linuxmacos)
  - [Optional: Windows Shortcuts](#optional-windows-shortcuts)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [CLI Commands](#cli-commands)
  - [Command-Line Flags](#command-line-flags)
- [Recent Bugfixes](#recent-bugfixes)
- [Development](#development)
- [License](#license)

Berserk Timer – a CLI timer with witness mode, and flexible duration input.
The goal was to create a simple Windows CLI timer that asks you what you have been doing for the last session. I couldn't find any free tool for Windows that suits my needs: flexibility, simplicity and no-adds in one. That's why I decided to create Berserk Timer. It helps me managing my time a lot so I decided to share it.

The tool provides:

- **CLI support**.
- **Customizable timers** with presets, and _witness_ mode.
- **Easy logging** for your activities.
- **Quick access** via the `brsrk` command, which can be used from any directory.

I hope this tool will make it easier for others to track time and stay productive. Enjoy Berserk Timer and feel free to contribute!

## Features

- **Flexible Duration Input:**
  - By default, the duration is entered in minutes (either whole or fractional, e.g., `1.5` means 1 minute 30 seconds).
  - The `--seconds` flag allows you to input the duration in seconds.
- **Presets:**
  Use the flags `-x`, `-s`, `-m`, `-l`, `-X`, or `-t` to select predefined durations (in minutes). You can add the presets into `config.json`
- **Witness Mode:**
  After the timer finishes (whether it was paused, quit, or stopped in another way), the user will be asked the question "What were you doing?" – you can enter text in any language (or type the safe word from config to cancel, default: `skip`) and in the end of the week there are a list of your activities for each day and hour.
- **Silent Mode:**
  The timer can be launched in mute mode (using the `--mute` flag), and during a running timer you can toggle silent mode on/off with the `m` command. In silent mode, the end-of-timer melody will not play. _(Note: CLI flags `--mute` and `--silent` are planned for upcoming release)_
- **Interfaces:**
  Both CLI and GUI modes are supported, but I personally prefer to use CLI whenever it is possible, so GUI is still very experimental and rude. Use the `-g` flag to start the graphical interface for your own risk.
- **Logging:**
  All events are recorded in the `logs` folder:
  - Main log – `logs/berserk.log`
  - Witness mode responses – `logs/witness_log_YYYY-MM-DD.txt`

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Quick Install (Windows)

1. **Clone the repository:**
   ```cmd
   git clone https://github.com/looksawful/berserk-timer.git
   cd berserk-timer
   ```

2. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Create your config file:**
   ```cmd
   copy config.example.json config.json
   ```
   Then edit `config.json` to customize your presets and messages.

4. **Run the timer:**
   ```cmd
   python -m src.main 25
   ```

### Quick Install (Linux/MacOS)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/looksawful/berserk-timer.git
   cd berserk-timer
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Create your config file:**
   ```bash
   cp config.example.json config.json
   ```
   Then edit `config.json` to customize your presets and messages.

4. **Run the timer:**
   ```bash
   python3 -m src.main 25
   ```

### Optional: Windows Shortcuts

For quick access from anywhere, you can use the provided batch files:

```cmd
# Run from anywhere after adding berserk-timer to PATH
brsrk.bat 25
```

Or create a shortcut:
1. Right-click `brsrk.bat` → Create Shortcut
2. Move shortcut to Desktop or Pin to Taskbar
3. (Optional) Change icon using `assets/icon.ico` if available

## Usage

### Basic Usage

**Start a timer (in minutes):**

```cmd
# 25 minutes (Pomodoro)
python -m src.main 25

# 1.5 minutes (1 minute 30 seconds)
python -m src.main 1.5
```

**Use presets:**

```cmd
# Extra Small (5 min)
python -m src.main -x

# Small (10 min)
python -m src.main -s

# Medium (15 min)
python -m src.main -m

# Large (20 min)
python -m src.main -l

# Extra Large (25 min)
python -m src.main -X

# Test preset (1 min)
python -m src.main -t
```

**Enable witness mode:**

```cmd
# Timer with witness mode
python -m src.main -w 25

# Witness mode asks "What were you doing?" after timer ends
# Type your activity or use safe word (default: "skip") to cancel
```

**Silent mode:**

```cmd
# Start timer without sound
python -m src.main --mute 25

# Toggle sound during timer with 'm' key
```

### CLI Commands

During timer execution, press:

- `p` - Pause/Resume timer (toggle)
- `n` - Restart timer from beginning
- `q` - Quit timer
- `z` - Zero timer (set to 0 and stop)
- `v` - View today's witness log
- `d` - Delete all logs
- `u` - Update timer duration
- `g` - Set/update goal
- `m` - Toggle silent mode

### Command-Line Flags

| Flag | Description |
|------|-------------|
| `-w, --witness` | Enable witness mode (asks what you did after timer) |
| `-g, --gui` | Launch GUI mode (experimental) |
| `-x, --xs` | Extra Small preset (5 min) |
| `-s, --small` | Small preset (10 min) |
| `-m, --medium` | Medium preset (15 min) |
| `-l, --large` | Large preset (20 min) |
| `-X, --xl` | Extra Large preset (25 min) |
| `-t, --test` | Test preset (1 min) |
| `--seconds` | Interpret duration as seconds instead of minutes |
| `--mute` | Start timer in silent mode |

## Recent Bugfixes

**Version 0.1.3-beta (Nov 23, 2025):**

1. **Added `safe_word` to config defaults**
   - The witness mode now includes a configurable safe word (default: `"skip"`)
   - Users can type the safe word instead of answering "What were you doing?"
   - Fallback ensures safe_word is always present even in old config files

2. **Fixed test preset duration**
   - Changed from `0.1` minutes (6 seconds) to `1` minute
   - More realistic test duration for development and debugging

3. **Message sanitization**
   - Empty strings are now automatically removed from witness mode messages
   - Prevents blank entries in witness logs

4. **Fixed premature logging**
   - "Timer ended" log now only appears when timer completes naturally
   - Previously logged even when user quit early

5. **Test coverage improvements**
   - Added `test_load_config_sanitizes_messages_and_adds_safe_word()`
   - Validates config loading, message sanitization, and safe_word presence

**Files Modified:**
- `src/config_manager.py` - Config defaults and validation
- `src/main.py` - Timer end logging fix
- `tests/test_config.py` - New test cases

## Development

### Tech Stack

- **Python:** 3.10+
- **CLI Framework:** Rich (beautiful terminal UI)
- **Audio:** Pygame (sound notifications)
- **Testing:** pytest + pytest-cov
- **Configuration:** JSON-based

### Setup Development Environment

1. **Clone and install:**

   ```bash
   git clone https://github.com/looksawful/berserk-timer.git
   cd berserk-timer
   pip install -r requirements.txt
   ```

2. **Run tests:**

   ```bash
   # Run all tests with verbose output
   pytest tests/ -v

   # Run with coverage report
   pytest tests/ --cov=src --cov-report=html

   # Open coverage report
   # Windows: start htmlcov/index.html
   # Linux: xdg-open htmlcov/index.html
   ```

3. **Project structure:**

   ```
   berserk-timer/
   ├── src/              # Source code
   │   ├── main.py       # Entry point
   │   ├── timer.py      # Timer logic
   │   ├── cli.py        # CLI interface
   │   ├── config_manager.py
   │   ├── logger.py
   │   └── witness.py
   ├── tests/            # Test suite
   ├── logs/             # Activity logs (gitignored)
   ├── config.json       # User config (gitignored)
   ├── config.example.json
   └── README.md
   ```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Update CHANGELOG.md
6. Commit: `git commit -m "feat: description"`
7. Push: `git push origin feature/your-feature`
8. Submit a pull request

### Commit Message Convention

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Build/config changes

### Roadmap

See [CHANGELOG.md](CHANGELOG.md) for version history and planned features.

**Upcoming:**
- [ ] Unified `--mute` / `--silent` CLI handling
- [ ] CSV/JSON export for witness logs
- [ ] Configurable audio files
- [ ] Improved GUI (currently experimental)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Created by [looksawful](https://github.com/looksawful)**
**Repository:** https://github.com/looksawful/berserk-timer
