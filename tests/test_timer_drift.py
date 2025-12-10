import time
from src.timer import Timer


def test_timer_drift_small_duration():
    duration = 1.0
    timer = Timer(duration=duration)
    timer.start()
    time.sleep(duration + 0.2)
    remaining = timer.get_remaining_time()
    assert remaining <= 0.1
    timer.stop()
