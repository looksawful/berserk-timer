import argparse
import sys
import random
from typing import Optional
from .config_manager import load_config
from .timer import Timer
from .cli import run_cli_timer, cli_witness_form
from .logger import log_event, log_witness_response, play_sound

ASCII_LOGO = r"""
███   ▄███▄   █▄▄▄▄   ▄▄▄▄▄   ▄███▄   █▄▄▄▄ █  █▀
█  █  █▀   ▀  █  ▄▀  █     ▀▄ █▀   ▀  █  ▄▀ █▄█
█ ▀ ▄ ██▄▄    █▀▀▌ ▄  ▀▀▀▀▄   ██▄▄    █▀▀▌  █▀▄
█  ▄▀ █▄   ▄▀ █  █  ▀▄▄▄▄▀    █▄   ▄▀ █  █  █  █
███   ▀███▀      █             ▀███▀     █     █
                ▀                       ▀     ▀
"""


def on_timer_end(timer: Timer, witness_mode: bool, config: dict, custom_phrase: Optional[str],
                 use_gui: bool = False, root: Optional[object] = None) -> None:
    play_sound()
    if witness_mode:
        safe_word = config.get("safe_word", "skip")
        response = cli_witness_form(safe_word)
        if response is not None:
            log_witness_response(response)
            print("Witness response logged.")
    message = custom_phrase if custom_phrase else random.choice(
        config.get("messages", []))
    if use_gui:
        run_gui_timer(timer, witness_mode, custom_phrase, config)
    else:
        print("\nAdvice:", message)
        print("Advice displayed.")


def main() -> None:
    print(ASCII_LOGO)
    parser = argparse.ArgumentParser(description="Berserk Timer Application")
    parser.add_argument("duration", type=float, nargs="?",
                        help="Duration (in minutes by default)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-x", action="store_true",
                       help="Use preset xs (5 minutes)")
    group.add_argument("-s", action="store_true",
                       help="Use preset s (10 minutes)")
    group.add_argument("-m", action="store_true",
                       help="Use preset m (15 minutes)")
    group.add_argument("-l", action="store_true",
                       help="Use preset l (20 minutes)")
    group.add_argument("-X", action="store_true",
                       help="Use preset xl (25 minutes)")
    group.add_argument("-t", action="store_true",
                       help="Use test preset (1 minute)")
    parser.add_argument("-w", action="store_true", help="Enable witness mode")
    parser.add_argument("-g", action="store_true",
                        help="Use GUI mode (experimental)")
    parser.add_argument("-c", type=str, help="Custom advice message")
    parser.add_argument("--seconds", action="store_true",
                        help="Interpret the provided duration as seconds innstead of minutes")
    args = parser.parse_args()
    config = load_config()
    duration: Optional[float] = None
    if args.duration is not None:
        duration = args.duration if args.seconds else args.duration * 60
    elif args.x:
        duration = config["presets"].get("xs") * 60
    elif args.s:
        duration = config["presets"].get("s") * 60
    elif args.m:
        duration = config["presets"].get("m") * 60
    elif args.l:
        duration = config["presets"].get("l") * 60
    elif args.X:
        duration = config["presets"].get("xl") * 60
    elif args.t:
        duration = config["presets"].get("test") * 60
    else:
        print("Please provide duration as a number or one of the preset flags (-x, -s, -m, -l, -X, -t).")
        sys.exit(1)
    if (args.x or args.s or args.m or args.l or args.X or args.t) and args.seconds:
        duration = duration * 60
    witness_mode: bool = args.w or config.get("witness_mode", False)
    custom_phrase: Optional[str] = args.c
    goal = input("Enter your goal (or leave empty): ").strip() or None

    if args.g:
        from .gui import run_gui_timer

    while True:
        timer_instance = Timer(duration, goal=goal)
        log_event(
            f"Timer started for {duration/60 if not args.seconds else duration} {'minutes' if not args.seconds else 'seconds'}. Witness mode: {witness_mode}. Custom message: {custom_phrase}. Goal: {goal}")
        timer_instance.start()
        log_event("Timer ended.")
        if args.g:
            root = run_gui_timer(
                timer_instance, witness_mode, custom_phrase, config)
            on_timer_end(timer_instance, witness_mode, config,
                         custom_phrase, use_gui=True, root=root)
            from tkinter import messagebox
            restart = messagebox.askyesno(
                "Restart Timer", "Do you want to restart the timer?")
            if restart:
                continue
            else:
                break
        else:
            user_exited = run_cli_timer(timer_instance)
            if user_exited:
                log_event("Timer exited by user.")
                print("Exiting the timer...")
                sys.exit(0)
            on_timer_end(timer_instance, witness_mode,
                         config, custom_phrase, use_gui=False)
            restart_choice = input("Restart timer? (y/n): ").lower().strip()
            if restart_choice == 'y':
                continue
            else:
                break
        
    log_event("Application terminated.")


if __name__ == "__main__":
    main()
