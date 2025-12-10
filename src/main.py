import argparse
import atexit
import logging
import random
import sys
import threading
import time
from typing import Optional, Tuple

from .ascii_art import ASCII_LOGO, AUTHOR_SIGNATURE
from .cli import cli_witness_form, run_cli_timer, validate_duration
from .config_manager import load_config
from .constants import MAX_TIMER_SECONDS
from .logger import (
    get_sound_duration,
    get_sound_path,
    log_event,
    log_timer_end,
    log_timer_start,
    log_witness_response,
    play_sound,
    set_mute,
    stop_sound,
)
from .screen_manager import cleanup_screen, init_screen
from .timer import Timer, TimerDurationError
from .version import __version__


def show_help() -> None:
    print(ASCII_LOGO)
    print(
        "\nBerserk Timer - A CLI timer with witness mode and flexible duration input.\n"
    )
    print("USAGE:")
    print("  python -m src.main [OPTIONS] [DURATION]\n")
    print("OPTIONS:")
    print("  -h, --help, /?         Show this help message and exit")
    print("  -x, --xs               Extra Small preset (5 minutes)")
    print("  -s, --small            Small preset (10 minutes)")
    print("  -m, --medium           Medium preset (15 minutes)")
    print("  -l, --large            Large preset (20 minutes)")
    print("  -X, --xl               Extra Large preset (25 minutes)")
    print("  -t, --test             Test preset (1 minute)")
    print("  -w, --witness          Enable witness mode (activity logging)")
    print("  -c MESSAGE             Custom advice message")
    print("  --sound FILE           Sound file to play (alert1-4.wav)")
    print("  --seconds              Interpret duration as seconds instead of minutes")
    print("  --mute                 Launch in silent mode\n")
    print("LIMITS:")
    print(
        f"  Maximum duration: {MAX_TIMER_SECONDS // 3600} hours ({MAX_TIMER_SECONDS // 60} minutes)\n"
    )
    print("EXAMPLES:")
    print("  python -m src.main 25              # 25 minute timer")
    print("  python -m src.main -X -w           # 25 min with witness mode")
    print("  python -m src.main 90 --seconds    # 90 second timer\n")
    print("DURING TIMER:")
    print("  p - Pause/resume       q - Quit (with confirmation)")
    print("  x - Zero timer         r - Restart timer")
    print("  v - View today's log   d - Delete today's log")
    print("  u - Update duration    g - Set/change goal")
    print("  m - Toggle silent      s - Audio settings")
    print("  h - Show help\n")
    sys.exit(0)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Berserk Timer Application", add_help=False
    )
    parser.add_argument(
        "duration",
        type=float,
        nargs="?",
        help="Duration (in minutes by default, or seconds if --seconds is specified)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-x", action="store_true", help="Use preset xs (5 minutes)")
    group.add_argument("-s", action="store_true", help="Use preset s (10 minutes)")
    group.add_argument("-m", action="store_true", help="Use preset m (15 minutes)")
    group.add_argument("-l", action="store_true", help="Use preset l (20 minutes)")
    group.add_argument("-X", action="store_true", help="Use preset xl (25 minutes)")
    group.add_argument("-t", action="store_true", help="Use test preset (1 minute)")
    parser.add_argument("-w", action="store_true", help="Enable witness mode")
    parser.add_argument("-c", type=str, help="Custom advice message")
    parser.add_argument(
        "--sound", type=str, help="Sound file to play (e.g., alert1.wav, alert2.wav)"
    )
    parser.add_argument(
        "--seconds", action="store_true", help="Interpret duration as seconds"
    )
    parser.add_argument("--mute", action="store_true", help="Launch in silent mode")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode: don't clear screen (canvas mode for debugging)",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        dest="show_help",
        help="Show help information and exit",
    )
    return parser.parse_known_args()[0]


def calculate_duration(args: argparse.Namespace, config: dict) -> Optional[float]:
    if args.duration is not None:
        factor = 1 if args.seconds else 60
        duration = args.duration * factor
        is_valid, error_msg = validate_duration(duration)
        if not is_valid:
            print(f"Error: {error_msg}")
            sys.exit(1)
        return duration

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


def on_timer_end(
    timer: Timer,
    witness_mode: bool,
    config: dict,
    custom_phrase: Optional[str],
    goal: Optional[str] = None,
) -> Tuple[float, float]:
    log_timer_end()
    timer_end_time = time.time()
    timer_end_perf = time.perf_counter()

    stop_repeating_alert = threading.Event()

    def repeating_alert():
        if timer.is_silent():
            return

        sound_file = timer.get_sound_file()
        current_volume = timer.get_volume()
        max_volume = 10

        while not stop_repeating_alert.is_set():
            play_sound(sound_file, current_volume)

            sound_path = get_sound_path(sound_file)
            sound_duration = get_sound_duration(sound_path)
            if sound_duration > 0:
                elapsed = 0
                while elapsed < sound_duration and not stop_repeating_alert.is_set():
                    time.sleep(0.1)
                    elapsed += 0.1
            else:
                time.sleep(3)

            if stop_repeating_alert.is_set():
                break

            if current_volume < max_volume:
                current_volume = min(current_volume + 1, max_volume)

    alert_thread = threading.Thread(target=repeating_alert, daemon=True)
    alert_thread.start()

    if witness_mode:
        safe_word = config.get("safe_word", "skip")
        response, final_timer_end_time = cli_witness_form(
            safe_word, timer, goal, timer_end_time, stop_repeating_alert=stop_repeating_alert
        )

        stop_repeating_alert.set()
        stop_sound()

        if response and response != "Witness skipped.":
            log_witness_response(response)

        return final_timer_end_time or timer_end_time, timer_end_perf
    else:
        stop_repeating_alert.set()

        messages = config.get("messages", [])
        if messages:
            message = custom_phrase or random.choice(messages)
            logging.info(f"Advice: {message}")
            print(f"\n💡 {message}")

        return timer_end_time, timer_end_perf


def run_timer_loop(
    args: argparse.Namespace,
    config: dict,
    duration: Optional[float],
    witness_mode: bool,
    custom_phrase: Optional[str],
    goal: Optional[str],
    interactive_mode: bool,
) -> None:
    first_iteration = True
    max_duration_minutes = MAX_TIMER_SECONDS / 60

    while True:
        if not first_iteration:
            while True:
                # print(f"\n[Max: {max_duration_minutes:.0f} minutes]")
                user_input = input("Enter timer duration in minutes: ").strip()
                if not user_input:
                    logging.error("Duration is required. Please enter a number.")
                    continue
                try:
                    duration_minutes = float(user_input)
                    duration = duration_minutes * 60
                    is_valid, error_msg = validate_duration(duration)
                    if not is_valid:
                        print(f"Error: {error_msg}")
                        continue
                    break
                except ValueError:
                    logging.error("Invalid input. Please enter a numeric value.")
            goal = input("Enter your goal (or leave empty): ").strip() or None

        if interactive_mode:
            display_duration = duration / 60 if duration else 0
            unit = "minutes"
        else:
            display_duration = (
                duration if args.seconds else (duration / 60 if duration else 0)
            )
            unit = "seconds" if args.seconds else "minutes"

        log_event(
            f"Timer started for {display_duration} {unit}. Witness mode: {witness_mode}. Custom message: {custom_phrase}. Goal: {goal}"
        )

        log_timer_start(duration / 60, goal)

        if not duration:
            logging.error("Error: Duration cannot be None.")
            sys.exit(1)

        sound_file = (
            args.sound
            if hasattr(args, "sound") and args.sound
            else config.get("sound_file", "alert1.wav")
        )
        volume = config.get("volume", 5)

        try:
            timer_instance = Timer(
                duration, goal=goal, sound_file=sound_file, volume=volume
            )
        except TimerDurationError as e:
            print(f"Error creating timer: {e}")
            sys.exit(1)

        if args.mute:
            timer_instance.set_volume(0)

        timer_instance.start()

        user_exited = run_cli_timer(timer_instance)
        if user_exited:
            log_event("Timer exited by user.")
            logging.info("Exiting the timer...")
            sys.exit(0)

        if timer_instance.was_zeroed() or timer_instance.get_remaining_time() == 0:
            if timer_instance.was_zeroed():
                log_event("Timer zeroed by user.")
            else:
                log_event("Timer ended.")

            timer_end_time, timer_end_perf = on_timer_end(
                timer_instance, witness_mode, config, custom_phrase, goal
            )
        else:
            continue

        elapsed_seconds = int(time.perf_counter() - timer_end_perf)
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            elapsed_str = f" (Timer ended {hours}h {minutes}m {seconds}s ago)"
        elif minutes > 0:
            elapsed_str = f" (Timer ended {minutes}m {seconds}s ago)"
        elif seconds > 0:
            elapsed_str = f" (Timer ended {seconds}s ago)"
        else:
            elapsed_str = ""

        restart_choice = input(f"\nRestart timer?{elapsed_str} (y/n): ").lower().strip()
        if restart_choice not in ("y", "yes"):
            break
        first_iteration = False


def main() -> None:
    if sys.platform.startswith("win"):
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    args = parse_arguments()

    debug_mode = hasattr(args, "debug") and args.debug
    screen = init_screen(use_alternate_buffer=True, debug_mode=debug_mode)

    atexit.register(cleanup_screen)

    print(ASCII_LOGO)
    print(AUTHOR_SIGNATURE)
    print(f"version: {__version__}")

    print("\nINSTRUCTIONS:")
    print("  • Set timer duration in minutes")
    print(
        "  • Presets: -x (5min), -s (10min), -m (15min), -l (20min), -X (25min), -t (1min test)"
    )
    print(f"  • Maximum duration: {MAX_TIMER_SECONDS // 3600} hours")
    print("  • Set your goal for this session (if witness mode enabled, or skip)")
    print("  • Choose sound: --sound alert1.wav (or alert2/alert3/alert4)")
    print("  • Set volume in config.json (1-10 scale, default: 5)")
    print("  • During timer:")
    print("    - Press 'p' to pause/resume")
    print("    - Press 'q' to quit")
    print("    - Press 'x' to zero the timer")
    print("    - Press 'r' to restart")
    print("    - Press 'v' to view today's log")
    print("    - Press 'd' to delete today's log")
    print("    - Press 'u' to update duration")
    print("    - Press 'g' to set/change goal")
    print("    - Press 'm' to toggle silent mode")
    print("    - Press 's' to open audio settings (sound/volume)")
    print("\n" + "-" * 60 + "\n")

    if (
        hasattr(args, "show_help")
        and args.show_help
        or any(arg in sys.argv for arg in ["/h", "/?"])
    ):
        show_help()

    config = load_config()

    interactive_mode = not any(
        [args.duration, args.x, args.s, args.m, args.l, args.X, args.t]
    )

    max_duration_minutes = MAX_TIMER_SECONDS / 60

    if not interactive_mode:
        duration = calculate_duration(args, config)
        if not duration:
            print(
                "Please provide a duration as a number or one of the preset flags (-x, -s, -m, -l, -X, -t)."
            )
            sys.exit(1)
    else:
        DEFAULT_DURATION_MINUTES = 5
        while True:
            try:
                duration_input = input(
                    f"\nEnter timer duration in minutes [max {max_duration_minutes:.0f}] (or press Enter for {DEFAULT_DURATION_MINUTES} min default): "
                ).strip()
                if not duration_input:
                    confirmation = (
                        input(
                            f"Use default {DEFAULT_DURATION_MINUTES} minutes? (y/n): "
                        )
                        .strip()
                        .lower()
                    )
                    if confirmation in ("y", "yes", ""):
                        duration_minutes = DEFAULT_DURATION_MINUTES
                        print(
                            f"Using default duration: {DEFAULT_DURATION_MINUTES} minutes"
                        )
                        duration = duration_minutes * 60
                        break
                    else:
                        continue
                duration_minutes = float(duration_input)
                duration = duration_minutes * 60

                is_valid, error_msg = validate_duration(duration)
                if not is_valid:
                    print(f"Error: {error_msg}")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

    try:
        goal = (
            input("\nWhat are you planning to do? (or press Enter to skip): ").strip()
            or None
        )
    except (EOFError, KeyboardInterrupt):
        goal = None

    set_mute(args.mute)
    witness_mode = args.w or config.get("witness_mode", False)
    run_timer_loop(args, config, duration, witness_mode, args.c, goal, interactive_mode)
    log_event("Application terminated.")


if __name__ == "__main__":
    main()
