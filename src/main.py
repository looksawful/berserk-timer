# TODO import show_witness_form after witness-mode for gui is solved

import argparse
import sys
import random

from .config_manager import load_config
from .timer import Timer
from .cli import run_cli_timer, cli_witness_form
from .gui import run_gui_timer, show_message
from .logger import log_event, log_witness_response, play_sound


def on_timer_end(witness_mode, config, custom_phrase, use_gui=False, root=None):
    play_sound()

    if witness_mode:
        response = cli_witness_form()
# use this instead of response after implementing gui-witness
    #     if use_gui:
    #         response = show_witness_form(root)
    #     else:
    #         response = cli_witness_form()
    #     log_witness_response(response)
        log_witness_response(response)
        print("Witness response logged.")
    else:
        message = custom_phrase if custom_phrase else random.choice(
            config.get("messages", []))
        if use_gui:
            show_message(message, root)
        else:
            print("\nAdvice:", message)
        print("Advice displayed.")


def main():
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
                        help="Use GUI mode(experimental, don't expect it to work fine)")
    parser.add_argument("-c", type=str, help="Custom advice message")
    parser.add_argument("--seconds", action="store_true",
                        help="Interpret the provided duration as seconds instead of minutes")

    args = parser.parse_args()

    config = load_config()
    duration = None

    if args.duration is not None:
        duration = args.duration if args.seconds else args.duration * 60
    elif args.x:
        duration = config["presets"].get("xs")
    elif args.s:
        duration = config["presets"].get("s")
    elif args.m:
        duration = config["presets"].get("m")
    elif args.l:
        duration = config["presets"].get("l")
    elif args.X:
        duration = config["presets"].get("xl")
    elif args.t:
        duration = config["presets"].get("test")
    else:
        print("Please provide duration as a number or one of the preset flags (-x, -s, -m, -l, -X, -t).")
        sys.exit(1)

    if (args.x or args.s or args.m or args.l or args.X or args.t) and args.seconds:
        duration = duration * 60

    witness_mode = args.w or config.get("witness_mode", False)
    custom_phrase = args.c

    total_seconds = duration
    timer = Timer(total_seconds)

    log_event(
        f"Timer started for {duration/60 if not args.seconds else duration} {'minutes' if not args.seconds else 'seconds'}. Witness mode: {witness_mode}. Custom message: {custom_phrase}")
    timer.start()

    if args.g:
        root = run_gui_timer(timer, witness_mode, custom_phrase, config)
        # Передаем None вместо root, если окно уже уничтожено
        on_timer_end(witness_mode, config, custom_phrase,
                     use_gui=True, root=None)
    else:
        user_exited = run_cli_timer(timer)
        if user_exited:
            log_event("Timer exited by user.")
            if not witness_mode:
                print("Exiting the timer...")
                sys.exit(0)
        on_timer_end(witness_mode, config, custom_phrase, use_gui=False)

    log_event("Timer ended.")


if __name__ == "__main__":
    main()
