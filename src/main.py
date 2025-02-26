import argparse
import sys
import random
from typing import Optional
from .config_manager import load_config
from .timer import Timer
from .cli import run_cli_timer, cli_witness_form
from .gui import run_gui_timer
from .logger import log_event, log_witness_response, play_sound, set_mute

ASCII_LOGO: str = r"""
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
"""


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Berserk Timer Application")
    parser.add_argument("duration", type=float, nargs="?",
                        help="Duration (in minutes by default, or seconds if --seconds is specified)")
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
    parser.add_argument("-g", action="store_true", help="Use GUI mode")
    parser.add_argument("-c", type=str, help="Custom advice message")
    parser.add_argument("--seconds", action="store_true",
                        help="Interpret duration as seconds")
    parser.add_argument("--mute", action="store_true",
                        help="Launch in silent mode")
    return parser.parse_args()


def calculate_duration(args: argparse.Namespace, config: dict) -> Optional[float]:
    if args.duration is not None:
        factor = 1 if args.seconds else 60
        return args.duration * factor
    presets = config["presets"]
    if args.x:
        return presets.get("xs", 5) * 60
    if args.s:
        return presets.get("s", 10) * 60
    if args.m:
        return presets.get("m", 15) * 60
    if args.l:
        return presets.get("l", 20) * 60
    if args.X:
        return presets.get("xl", 25) * 60
    if args.t:
        return presets.get("test", 1) * 60
    return None


def on_timer_end(timer: Timer, witness_mode: bool, config: dict, custom_phrase: Optional[str], use_gui: bool = False, root: Optional[object] = None) -> None:
    import threading
    if not timer.is_silent():
        threading.Thread(target=play_sound, daemon=True).start()
    if witness_mode:
        safe_word = config.get("safe_word", "skip")
        response = cli_witness_form(safe_word)
        if response:
            log_witness_response(response)
    message = custom_phrase or random.choice(config.get("messages", []))
    if use_gui:
        if root:
            from tkinter import messagebox
            messagebox.showinfo("Advice", f"Advice: {message}")
        else:
            run_gui_timer(timer, witness_mode, custom_phrase, config)
    else:
        print("\nAdvice:", message)


def run_timer_loop(args: argparse.Namespace, config: dict, duration: Optional[float], witness_mode: bool, custom_phrase: Optional[str], goal: Optional[str], interactive_mode: bool) -> None:
    first_iteration = True
    while True:
        if not first_iteration or interactive_mode:
            while True:
                user_input = input("Enter timer duration in minutes: ").strip()
                if not user_input:
                    print("Duration is required. Please enter a number.")
                    continue
                try:
                    duration_minutes = float(user_input)
                    duration = duration_minutes * 60
                    break
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")
            goal = input("Enter your goal (or leave empty): ").strip() or None

        if interactive_mode:
            display_duration = duration / 60 if duration else 0
            unit = "minutes"
        else:
            display_duration = duration if args.seconds else (
                duration / 60 if duration else 0)
            unit = "seconds" if args.seconds else "minutes"

        log_event(
            f"Timer started for {display_duration} {unit}. Witness mode: {witness_mode}. Custom message: {custom_phrase}. Goal: {goal}")
        if not duration:
            print("Error: Duration cannot be None.")
            sys.exit(1)

        timer_instance = Timer(duration, goal=goal)
        timer_instance.start()
        log_event("Timer ended.")

        if args.g:
            print("Sorry, GUI mode is not available in this version.")
            sys.exit(1)
        else:
            user_exited = run_cli_timer(timer_instance)
            if user_exited:
                log_event("Timer exited by user.")
                print("Exiting the timer...")
                sys.exit(0)
            on_timer_end(timer_instance, witness_mode,
                         config, custom_phrase, use_gui=False)
            restart_choice = input("Restart timer? (y/n): ").lower().strip()
            if restart_choice != 'y' and restart_choice != 'д':
                break
        first_iteration = False


def main() -> None:
    print(ASCII_LOGO)
    args = parse_arguments()
    config = load_config()

    if args.g:
        print("GUI mode is not available in this version.")
        sys.exit(1)

    interactive_mode = not any(
        [args.duration, args.x, args.s, args.m, args.l, args.X, args.t])
    if not interactive_mode:
        duration = calculate_duration(args, config)
        if not duration:
            print(
                "Please provide a duration as a number or one of the preset flags (-x, -s, -m, -l, -X, -t).")
            sys.exit(1)
        goal = input("Enter your goal (or leave empty): ").strip() or None
    else:
        duration = None
        goal = None

    set_mute(args.mute)
    witness_mode = args.w or config.get("witness_mode", False)
    run_timer_loop(args, config, duration, witness_mode,
                   args.c, goal, interactive_mode)
    log_event("Application terminated.")


if __name__ == "__main__":
    main()
