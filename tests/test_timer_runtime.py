import threading
import time

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


def test_start_is_idempotent_while_timer_is_running():
    timer = Timer(duration=1.0)
    timer.start()
    first_thread = timer._thread

    timer.start()

    assert timer._thread is first_thread
    timer.stop()


def test_pause_resume_stop_race_does_not_crash():
    timer = Timer(duration=1.0)
    timer.start()

    def pauser():
        for _ in range(5):
            timer.pause()
            time.sleep(0.01)
            timer.resume()

    threads = [threading.Thread(target=pauser) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    timer.stop()
    assert not timer.is_running()


def test_stop_while_paused_completes():
    timer = Timer(duration=1.0)
    timer.start()
    timer.pause()
    timer.stop()
    assert not timer.is_running()
