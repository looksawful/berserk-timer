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

- [Berserk Timer 0.1.3-beta](#berserk-timer-013-beta)
  - [Features](#features)
  - [Recent Bugfixes](#recent-bugfixes)
  - [Installing on Windows](#installing-on-windows)
    - [Optional](#optional)
  - [Running](#running)
    - [Windows](#windows)
    - [Linux](#linux)
    - [MacOS](#macos)
  - [Development](#development)

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

## Installing on Windows

1. Install `git` from `https://git-scm.com/download/win`
2. Open a terminal to the folder you want Berserk in and run
`git clone https://github.com/looksawful/BerserkTimer`
3. Then `cd` into folder and run `brsrk-cli.bat` for cli, or `brsrk-gui.bat` for gui

### Optional

_You may want to add a shortcut to run brsrk from Windows Taskbar, but it's impossible to use .bat scripts like that, so while there is no normal installer I personally prefer this trick:_
4. Create an empty shortcut in the berserk-timer directory or anywhere you like it and force rename it to `.exe`
5. After renaming in file properties add In the properties of the shortcut add `C:\Windows\System32\cmd.exe /c C:\Users\awful\Documents\Code\berserk-timer\brsrk.bat`
5. Add an icon from `.\berserk-timer\assets\icon.ico`

## Running

### Windows

From the berserk-timer directory, run:

- Example: 1.5 minutes (i.e., 1 minute 30 seconds):

  ```cmd
  python -m src.main 1.5
  ```

### Linux

From the berserk-timer directory, run:

- Example: 1.5 minutes (i.e., 1 minute 30 seconds):

  ```bash
  python3 -m src.main 1.5
  ```

### MacOS

From the berserk-timer directory, run:

- Example: 1.5 minutes (i.e., 1 minute 30 seconds):

  ```bash
  python3 -m src.main 1.5
  ```

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

**Tech Stack:** Python 3.10+, Rich (CLI), Pygame (audio), pytest (testing)

**Running Tests:**

``bash
pytest tests/ -v --cov=src
``

**Contributing:**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Run tests before committing
4. Submit a pull request

**Roadmap:**

- [ ] Add `--mute` and `--silent` CLI flags
- [ ] Improve GUI interface (experimental)
- [ ] Add configurable audio files
- [ ] Export witness logs to CSV/JSON

For detailed development tasks, see `TODO/berserk-timer-TODO.md` in the project root.
