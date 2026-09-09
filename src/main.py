import argparse
import atexit
import sys

from .ascii_art import ASCII_LOGO, AUTHOR_SIGNATURE
from .audio import set_mute
from .config_manager import get_default_config_path, load_config
from .constants import MAX_TIMER_SECONDS
from .logger import log_event
from .screen_manager import cleanup_screen, init_screen
from .session import on_timer_end as on_timer_end
from .session import run_timer_loop as run_timer_loop
from .timer import TimerDurationError, validate_duration
from .version import __version__


def configure_stdout_encoding() -> None:
    """Use UTF-8 on Windows without replacing or detaching the host stream."""
    if not sys.platform.startswith("win"):
        return

    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8")
        except (OSError, ValueError, AttributeError):
            pass


def show_help() -> None:
    print(ASCII_LOGO)
    print(
        "\nBerserk Timer - A CLI timer with witness mode and flexible duration input.\n"
    )
    print("USAGE:")
    print("  python -m src.main [OPTIONS] [DURATION]\n")
    print("OPTIONS:")
    print("  -h, --help, /h, /?    Show this help message and exit")
    print("  -x, --xs               Extra Small preset (5 minutes)")
    print("  -s, --small            Small preset (10 minutes)")
    print("  -m, --medium           Medium preset (15 minutes)")
    print("  -l, --large            Large preset (20 minutes)")
    print("  -X, --xl               Extra Large preset (25 minutes)")
    print("  -t, --test             Test preset (1 minute)")
    print("  -w, --witness          Enable witness mode (activity logging)")
    print("  -c MESSAGE             Custom advice message")
    print("  --sound FILE           Sound file to play (alert1-5.wav)")
    print("  --seconds              Interpret duration as seconds instead of minutes")
    print("  --mute                 Launch in silent mode\n")
    print("LIMITS:")
    print(
        f"  Maximum duration: {MAX_TIMER_SECONDS // 3600} hours "
        f"({MAX_TIMER_SECONDS // 60} minutes)\n"
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
    argv = ["--help" if arg in {"/h", "/?"} else arg for arg in sys.argv[1:]]
    return parser.parse_args(argv)


def calculate_duration(args: argparse.Namespace, config: dict) -> float | None:
    if args.duration is not None:
        factor = 1 if args.seconds else 60
        duration = args.duration * factor
        try:
            validate_duration(duration)
        except TimerDurationError as exc:
            print(f"Error: {exc}")
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


def main() -> None:
    configure_stdout_encoding()

    args = parse_arguments()

    if args.show_help:
        show_help()

    init_screen(use_alternate_buffer=True, debug_mode=args.debug)
    atexit.register(cleanup_screen)

    print(ASCII_LOGO)
    print(AUTHOR_SIGNATURE)
    print(f"version: {__version__}")

    print("\nINSTRUCTIONS:")
    print("  • Set timer duration in minutes")
    print(
        "  • Presets: -x (5min), -s (10min), -m (15min), -l (20min), "
        "-X (25min), -t (1min test)"
    )
    print(f"  • Maximum duration: {MAX_TIMER_SECONDS // 3600} hours")
    print("  • Set your goal for this session (if witness mode enabled, or skip)")
    print("  • Choose sound: --sound alert1.wav (or alert2/alert3/alert4/alert5)")
    print("  • Set volume in the user config file (0-10 scale, default: 5)")
    print(f"  • Config: {get_default_config_path()}")
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

    config = load_config()

    interactive_mode = not any(
        [
            args.duration is not None,
            args.x,
            args.s,
            args.m,
            args.l,
            args.X,
            args.t,
        ]
    )

    max_duration_minutes = MAX_TIMER_SECONDS / 60

    if not interactive_mode:
        duration = calculate_duration(args, config)
        if duration is None:
            print(
                "Please provide a duration as a number or one of the preset flags "
                "(-x, -s, -m, -l, -X, -t)."
            )
            sys.exit(1)
    else:
        default_duration_minutes: float = 5.0
        while True:
            try:
                duration_input = input(
                    "\nEnter timer duration in minutes "
                    f"[max {max_duration_minutes:.0f}] "
                    f"(or press Enter for {default_duration_minutes:g} min default): "
                ).strip()
                if not duration_input:
                    confirmation = (
                        input(
                            f"Use default {default_duration_minutes:g} minutes? (y/n): "
                        )
                        .strip()
                        .lower()
                    )
                    if confirmation in ("y", "yes", ""):
                        duration_minutes = default_duration_minutes
                        print(
                            f"Using default duration: {default_duration_minutes:g} minutes"
                        )
                        duration = duration_minutes * 60
                        break
                    continue
                duration_minutes = float(duration_input)
                duration = duration_minutes * 60

                try:
                    validate_duration(duration)
                except TimerDurationError as exc:
                    print(f"Error: {exc}")
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
