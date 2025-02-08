```
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
                                 ▀

```

# Berserk Timer 0.1.1-beta

- [Berserk Timer 0.1.1-beta](#berserk-timer-011-beta)
  - [Features](#features)
  - [Installing on Windows](#installing-on-windows)
    - [optional](#optional)
  - [Running](#running)
    - [Windows](#windows)
    - [Linux](#linux)
    - [MacOS](#macos)


Berserk Timer – a CLI timer with witness mode, and flexible duration input.
The goal was to create a simple Windows CLI timer that asks you what you havebeen doing for the last N-minutes. I couldn't find any free tool that suits my needs: flexibility, simplicity and no-adds in one. That's why I decided to create Berserk Timer. It helps me managing my time a lot so I decided to share it.

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
  Use the flags `-x`, `-s`, `-m`, `-l`, `-X`, or `-t` to select predefined durations (in minutes). You can add the presets into config.json
- **Witness Mode:**
  After the timer finishes (whether it was paused, quit, or stopped in another way), the user will be asked the question "What were you doing?" – you can enter text in any language (or type 'skip' to cancel) and in the end of the week there are a list of your activities for each day and hour.
- **Interfaces:**
  Both CLI and GUI modes are supported, but I personally prefer to use CLI whenerever it is possible, so GUI is still very experimental and rude. Use the `-g` flag to start the graphical interface for your own risk.
- **Logging:**
  All events are recorded in the `logs` folder:
  - Main log – `logs/berserk.log`
  - Witness mode responses – `logs/witness_log_YYYY-MM-DD.txt`

## Installing on Windows

1. Install `git` from `https://git-scm.com/download/win`
2. Open a terminal to the folder you want Berserk in and run
`git clone https://github.com/looksawful/BerserkTimer`
3. Then `cd` into folder and run `brsrk-cli.bat` for cli, or `brsrk-gui.bat` for gui

### optional
_You may want to add a shortcut to run brsrk from Windows Taskbar, but it's impossible to use .bat scripts like that, so while there is no normall installer I personally prefer this trick:_
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
