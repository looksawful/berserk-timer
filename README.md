███   ▄███▄   █▄▄▄▄   ▄▄▄▄▄   ▄███▄   █▄▄▄▄ █  █▀ 
█  █  █▀   ▀  █  ▄▀  █     ▀▄ █▀   ▀  █  ▄▀ █▄█   
█ ▀ ▄ ██▄▄    █▀▀▌ ▄  ▀▀▀▀▄   ██▄▄    █▀▀▌  █▀▄   
█  ▄▀ █▄   ▄▀ █  █  ▀▄▄▄▄▀    █▄   ▄▀ █  █  █  █  
███   ▀███▀     █             ▀███▀     █     █   
               ▀                       ▀     ▀    
                                                  
       ▄▄▄▄▀ ▄█ █▀▄▀█ ▄███▄   █▄▄▄▄               
    ▀▀▀ █    ██ █ █ █ █▀   ▀  █  ▄▀               
        █    ██ █ ▄ █ ██▄▄    █▀▀▌                
       █     ▐█ █   █ █▄   ▄▀ █  █                
      ▀       ▐    █  ▀███▀     █                 
                  ▀            ▀


# Berserk Timer

Berserk Timer – a CLI timer with witness mode, and flexible duration input.
The goal is to create a simple Windows CLI timer that will ask you what were you done for the last N minutes.

I couldn't find any tool that suits my needs: flexibility, simplicity, and functionality in one. That's why I decided to create Berserk Timer. It helps me managing my time a lot so I decided to share it.

The tool provides:

- **CLI support**.
- **Customizable timers** with presets, and witness mode.
- **Easy logging** for your activities.
- **Quick access** via the `brsk` command, which can be used from any directory.

I hope this tool will make it easier for others to track time and stay productive. Enjoy Berserk Timer and feel free to contribute!

## Features

- **Flexible Duration Input:**
  - By default, the duration is entered in minutes (either whole or fractional, e.g., `1.5` means 1 minute 30 seconds).
  - The `--seconds` flag allows you to input the duration in seconds.
- **Presets:**
  Use the flags `-x`, `-s`, `-m`, `-l`, `-X`, or `-t` to select predefined durations (in minutes). You can add the presets into config.json
- **Witness Mode:**
  After the timer finishes (whether it was paused, quit, or stopped in another way), the user will be asked the question "What were you doing?" – you can enter text in any language (e.g., Cyrillic) and in the end of the week there are a list of your activities for each day and hour.
- **Interfaces:**
  Both CLI and GUI modes are supported, but I personally prefer to use CLI whenerever it is possible, so GUI is still very experimental and rude. Use the `-g` flag to start the graphical interface for your own risk.
- **Logging:**
  All events are recorded in the `logs` folder:
  - Main log – `logs/berserk.log`
  - Witness mode responses – `logs/witness_log_YYYY-MM-DD.txt`

## Running

From the root directory, run:

- Example: 1.5 minutes (i.e., 1 minute 30 seconds):

  ```bash
  python -m src.main 1.5
  ```

  or just run `brsk` command, which can be used from any directory.

  
