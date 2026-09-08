# Berserk Timer 0.2.1-beta

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

_Logo generated via the TAAG Text to ASCII Art Generator (edge font); the CLI uses your terminal's monospace font._

## Berserk Timer - a CLI timer with witness mode, and flexible duration input

I needed a simple Windows CLI timer that asks "What have you been doing?" after each session. I couldn't find any free tool that combined flexibility, simplicity, and a no-ads policy. So I decided to create Berserk Timer. It helps me manage my time a lot, so I decided to share it.

### ⚠️ Compatibility Note (Please Read)

This project is currently in active development (**Beta**).

- ✅ **Windows:** Fully ready and tested. This is the primary platform.
- ❓ **Linux & MacOS:** **Untested and likely not working.** Since I primarily use Windows, I haven't been able to adapt the audio and system notifications for Unix-based systems yet. I am open to any suggestions, fixes, or Pull Requests to get Linux and Mac versions running!

> Engine note: the runtime currently uses the `Timer` class; `TimerCore` remains experimental and is not wired into the CLI yet.

### What's New in 0.2.1?

- Fixed `x` key to open the witness prompt (and stop repeating alert after `k`).
- True silent start when using `--mute` or `volume: 0`; logging falls back to stderr on read-only FS.
- Restart after completion now resets duration; volume range normalized to 0–10 with global mute override.

### What's New in 0.2.0?

I completely rewrote the internal engine (`TimerCore`).

- **Drift Compensation:** The timer now runs on a dedicated thread with precise time correction.
- **Responsive UI:** Separated the logic from the interface. Commands like Pause/Resume happen instantly.
- **Volume Control:** You can now set volume (0-10), not just mute/unmute.

### Features

1. **Flexible Duration Input:**
   - Type `1.5` for 1 minute 30 seconds.
   - Use `--seconds` flag to just type seconds.
2. **Witness Mode:**
   - After the timer finishes (or is stopped), it asks: _"What were you doing?"_
   - You can enter text in any language or type `skip`.
   - Logs are saved so you can review your week later.
3. **Presets:**
   - Quickly start timers using flags like `-s` (short), `-m` (medium), `-l` (long).
   - Fully customizable via `config.json`.
4. **Control & Audio:**
   - **Silent Mode:** Launch with `--mute`, set `volume: 0` in `config.json`, or toggle with `m` key.
   - **Volume:** Configurable volume levels 0-10 for the alert sound; global mute overrides per-timer volume until disabled.
   - Audio playback currently uses pygame (listed in requirements).
   - **Hotkeys:** Pause, Resume, or Restart on the fly.
5. **Logging:**
   - System log: `logs/berserk.log`
   - Activity log: `logs/witness_log_YYYY-MM-DD.txt`
   - Read-only environments fall back to stderr; witness logs will not be written if the filesystem is not writable.

### Installation (Windows)

1. **Clone the Repo:** Open your terminal in the desired folder and run:

   ```bash
   git clone https://github.com/looksawful/berserk-timer
   ```

2. **Dependencies:** Make sure you have Python installed. Then install requirements:

   ```bash
   cd berserk-timer
   pip install -r requirements.txt
   ```

   _(If `requirements.txt` doesn't exist yet, standard Python libs should suffice for now)._

3. **Run:** use `brsrk.bat`.

#### Optional: Create a Shortcut

Since `.bat` files can't be pinned easily to the Taskbar, I use this trick to make it look like a native app:

1. Create a standard shortcut to `brsrk.bat` (Right click -> Create shortcut).
2. Right-click the shortcut -> **Properties**.
3. In the **Target** field, change it to use `cmd.exe`. It should look like this:
   C:\Windows\System32\cmd.exe /c "C:\Users\YourName\Path\To\BerserkTimer\brsrk.bat"

4. Click **Change Icon** and select `assets/icon.ico` from the project folder.
5. Now you can pin it to the Taskbar!

### Configuration & Presets

You can customize the timer by editing `config.json` in the root folder.

**Default Presets:**

- `-x`: Extra short (Pomodoro break?)
- `-s`: Short
- `-m`: Medium
- `-l`: Long
- `-t`: Test

**Example config.json:**

```json
{
  "presets": {
    "x": 5,
    "s": 15,
    "m": 25,
    "l": 45
  },
  "default_volume": 5,
  "sound_file": "alert1.wav"
}
```

### Usage & Commands

**Starting the timer:**

```bash
# Standard run (duration in minutes)
python -m src.main 10

# Fractional minutes (1 min 30 sec)
python -m src.main 1.5

# Using a preset (e.g., Short)
python -m src.main -s

# Start in silent mode
python -m src.main 25 --mute
```

**While the timer is running:**

The new Core listens to key events (depending on your UI implementation):

- `p` or `Space`: **Pause/Resume**
- `r`: **Restart** timer from the beginning
- `m`: Toggle **Mute** (Silent mode)
- `s` or `Esc`: **Stop** timer (Triggers Witness Mode)
- `z`: **Zero** out timer (Ends immediately)

### For Linux Users (Experimental)

As stated, this might not work out of the box. Yyou can try:

```bash
python3 -m src.main 1.5
```

If you encounter audio errors, please check if you have the necessary system libraries for `playsound` or whichever audio lib is being used. Contributions are welcome!

Enjoy Berserk Timer and feel free to contribute!

## License

Berserk Timer is provided under a personal/non-commercial license. Highlights:
- Use and modify for personal, educational, and other non-commercial purposes with attribution.
- Commercial use, resale, or paid distribution requires my written permission.
- All alert sounds and other audio assets remain my property; keep them inside Berserk Timer and do not reuse or redistribute them separately.
- Third-party dependencies keep their own licenses (pygame is LGPL).

See [LICENSE](LICENSE) for the full terms.