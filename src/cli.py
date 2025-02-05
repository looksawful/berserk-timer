from .logger import view_today_log, delete_all_logs
import threading
import sys
import time
import select

try:
    import msvcrt

    def kbhit():
        return msvcrt.kbhit()

    def getch():  # type: ignore
        return msvcrt.getch().decode('utf-8')
except ImportError:
    import tty
    import termios

    def kbhit():
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        return dr != []

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)  # type: ignore
        try:
            tty.setraw(fd)  # type: ignore
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN,  # type: ignore
                              old_settings)
        return ch


def run_cli_timer(timer):
    exit_flag = False

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

    commands = {
        'p': pause_action,
        'r': resume_action,
        'q': stop_action,
        'z': zero_action,
        'n': restart_action,
        'v': view_log_action,
        'd': delete_logs_action
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
                    print("\nUnknown command. Press (p, r, q, z, n, v, d) only.")
            time.sleep(0.1)

    listener = threading.Thread(target=keyboard_listener, daemon=True)
    listener.start()

    while timer.is_running() and not exit_flag:
        print(
            f"Time remaining: {timer.get_remaining_time_str()}  "
            f"(p: pause, r: resume, q: quit, z: zero, n: restart, v: view log, d: delete logs)",
            end="\r"
        )
        time.sleep(0.1)

    print()
    return exit_flag


def cli_witness_form(safe_word):
    """
    Asks user to enter activity description in CLI after the timer ends.
    Input cannot be empty.
    If the user types the safe word, the function returns a special message.

    :param safe_word: The safe word that, when entered, cancels witness-mode.
    :return: User input or "Witness skipped." if safe word is entered.
    """
    while True:
        response = input(
            f"\nTimer finished. Please enter what you were doing (or type '{safe_word}' to cancel): "
        ).strip()
        if response.lower() == safe_word.lower():
            return "Witness skipped."
        if response:
            return response
        print(
            f"Input cannot be empty. Please provide a description of your activity, or type '{safe_word}' to cancel.")
