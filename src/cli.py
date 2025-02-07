from .logger import view_today_log, delete_all_logs
import threading
import sys
import time
import select

if sys.platform.startswith("win"):
    import msvcrt

    def kbhit():
        return msvcrt.kbhit()

    def getch():
        return msvcrt.getch().decode("utf-8")
else:
    import tty
    import termios

    def kbhit():
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        return dr != []

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN,
                              old_settings)
        return ch


def run_cli_timer(timer):
    exit_flag = False
    suspend_display = threading.Event()

    def pause_action():
        timer.pause()
        print("\nTimer paused. Press 'r' to resume.")

    def resume_action():
        timer.resume()
        print("\nTimer resumed.")

    def stop_action():
        nonlocal exit_flag
        timer.stop()
        exit_flag = True
        print("\nTimer stopped by user.")

    def zero_action():
        timer.zero()
        print("\nTimer zeroed.")

    def restart_action():
        timer.restart()
        print("\nTimer restarted.")

    def view_log_action():
        log_content = view_today_log()
        print("\nToday's Witness Log:")
        print(log_content)

    def delete_logs_action():
        delete_all_logs()
        print("\nAll logs deleted.")

    def update_duration_action():
        suspend_display.set()
        try:
            user_input = input("\nEnter new duration in minutes: ")
            new_duration = float(user_input) * 60
            timer.update_duration(new_duration)
            print(f"\nTimer duration updated to {new_duration/60} minutes.")
        except ValueError:
            print("\nInvalid input for duration update.")
        finally:
            suspend_display.clear()

    def set_goal_action():
        suspend_display.set()
        try:
            new_goal = input("\nEnter your goal: ")
            timer.set_goal(new_goal)
            print(f"\nGoal set to: {new_goal}")
        finally:
            suspend_display.clear()

    commands = {
        'p': pause_action,
        'r': resume_action,
        'q': stop_action,
        'z': zero_action,
        'n': restart_action,
        'v': view_log_action,
        'd': delete_logs_action,
        'u': update_duration_action,
        'g': set_goal_action
    }

    def keyboard_listener():
        nonlocal exit_flag
        while timer.is_running() and not exit_flag:
            if kbhit():
                try:
                    key = getch().lower()
                except UnicodeDecodeError:
                    continue
                if key in commands:
                    commands[key]()
                    if key == 'q' or key == 'z':
                        break
                else:
                    print("\nUnknown command. Press (p, r, q, z, n, v, d, u, g) only.")
            time.sleep(0.1)

    listener = threading.Thread(target=keyboard_listener, daemon=True)
    listener.start()

    # Вывод обновляемой строки с ANSI-последовательностью "\033[K" для очистки строки
    while timer.is_running() and not exit_flag:
        if not suspend_display.is_set():
            print(
                f"\r\033[KTime remaining: {timer.get_remaining_time_str()}  (p: pause, r: resume, q: quit, z: zero, n: restart, v: view log, d: delete logs, u: update duration, g: set goal)", end="")
        time.sleep(0.1)
    print()
    return exit_flag


def cli_witness_form(safe_word):
    while True:
        response = input(
            f"\nTimer finished. Please enter what you were doing (or type '{safe_word}' to cancel): ").strip()
        if response.lower() == safe_word.lower():
            return "Witness skipped."
        if response:
            return response
        print(
            f"Input cannot be empty. Please provide a description of your activity, or type '{safe_word}' to cancel.")
