import threading
import time
import pytest

from src.timer import Timer


def test_timer_stops_and_can_restart():
    timer = Timer(duration=1.0)
    timer.start()
    time.sleep(1.2)
    assert not timer.is_running()

    timer.start()
    assert timer.is_running()
    timer.stop()
    assert not timer.is_running()


def test_pause_resume_stop_race_does_not_crash():
    timer = Timer(duration=1.0)
    timer.start()

    def pauser():
        for _ in range(5):
            timer.pause()
            time.sleep(0.01)
            timer.resume()

    threads = [threading.Thread(target=pauser) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Stop after concurrent pause/resume should succeed
    timer.stop()
    assert not timer.is_running()


def test_stop_while_paused_completes():
    timer = Timer(duration=1.0)
    timer.start()
    timer.pause()
    timer.stop()
    assert not timer.is_running()
