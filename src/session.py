import argparse
import logging
import random
import sys
import threading
import time

from .audio import get_sound_duration, get_sound_path, play_sound, stop_sound
from .cli import cli_witness_form, run_cli_timer, validate_duration
from .config_manager import load_config
from .logger import log_event, log_timer_end, log_timer_start, log_witness_response
from .timer import Timer, TimerDurationError


def on_timer_end(
    timer: Timer,
    witness_mode: bool,
    config: dict,
    custom_phrase: str | None,
    goal: str | None = None,
) -> tuple[float, float]:
    log_timer_end()
    timer_end_time = time.time()
    timer_end_perf = time.perf_counter()

    stop_repeating_alert = threading.Event()

    def repeating_alert() -> None:
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
                elapsed = 0.0
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
            safe_word,
            timer,
            goal,
            timer_end_time,
            stop_repeating_alert=stop_repeating_alert,
        )

        stop_repeating_alert.set()
        stop_sound()

        if response and response != "Witness skipped.":
            log_witness_response(response)

        return final_timer_end_time or timer_end_time, timer_end_perf

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
    duration: float | None,
    witness_mode: bool,
    custom_phrase: str | None,
    goal: str | None,
    interactive_mode: bool,
) -> None:
    first_iteration = True

    while True:
        if not first_iteration:
            while True:
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

        if duration is None:
            logging.error("Error: Duration cannot be None.")
            sys.exit(1)

        if interactive_mode:
            display_duration = duration / 60
            unit = "minutes"
        else:
            display_duration = duration if args.seconds else duration / 60
            unit = "seconds" if args.seconds else "minutes"

        log_event(
            "Timer started for "
            f"{display_duration} {unit}. Witness mode: {witness_mode}. "
            f"Custom message: {custom_phrase}. Goal: {goal}"
        )
        log_timer_start(duration / 60, goal)

        sound_file = args.sound or config.get("sound_file", "alert1.wav")
        volume = config.get("volume", 5)

        try:
            timer_instance = Timer(
                duration, goal=goal, sound_file=sound_file, volume=volume
            )
        except TimerDurationError as exc:
            print(f"Error creating timer: {exc}")
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

            _timer_end_time, timer_end_perf = on_timer_end(
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
