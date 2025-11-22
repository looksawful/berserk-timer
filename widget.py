import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timer import Timer

def widget_timer(duration_seconds):
    timer = Timer(duration_seconds)
    timer.start()
    while timer.get_remaining_time() > 0:
        print(timer.get_remaining_time_str().encode("utf-8").decode("utf-8"), flush=True)
        time.sleep(1)
    print("00:00".encode("utf-8").decode("utf-8"), flush=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: widget.py <duration in minutes>", flush=True)
        sys.exit(1)
    try:
        duration_minutes = float(sys.argv[1])
    except ValueError:
        print("Invalid duration", flush=True)
        sys.exit(1)
    widget_timer(duration_minutes * 60)
