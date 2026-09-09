"""Unit tests for Timer class."""

import math
import unittest
import time

from src.timer import Timer, TimerDurationError


class TestTimer(unittest.TestCase):
    def test_timer_initialization(self):
        """Test timer initializes correctly with duration."""
        timer = Timer(duration=60.0)
        self.assertEqual(timer.duration, 60.0)
        self.assertEqual(timer.remaining, 60.0)
        self.assertIsNone(timer.goal)

    def test_timer_with_goal(self):
        """Test timer initializes correctly with goal."""
        timer = Timer(duration=120.0, goal="Write tests")
        self.assertEqual(timer.goal, "Write tests")

    def test_timer_rejects_nan_duration(self):
        with self.assertRaisesRegex(TimerDurationError, "finite"):
            Timer(duration=math.nan)

    def test_timer_rejects_nan_duration_update(self):
        timer = Timer(duration=10.0)

        with self.assertRaisesRegex(TimerDurationError, "finite"):
            timer.update_duration(math.nan)

    def test_timer_countdown(self):
        """Test timer countdown reduces remaining time."""
        timer = Timer(duration=2.0)
        timer.start()
        time.sleep(1.0)
        remaining = timer.get_remaining_time()
        self.assertLess(remaining, 2.0)
        self.assertGreater(remaining, 0.0)
        timer.stop()

    def test_timer_pause_resume(self):
        """Test pause and resume functionality."""
        timer = Timer(duration=5.0)
        timer.start()
        time.sleep(0.5)
        timer.pause()
        remaining_at_pause = timer.get_remaining_time()
        time.sleep(0.5)
        remaining_after_pause = timer.get_remaining_time()
        # Should not change significantly while paused
        self.assertAlmostEqual(remaining_at_pause, remaining_after_pause, delta=0.2)
        timer.resume()
        time.sleep(0.5)
        remaining_after_resume = timer.get_remaining_time()
        self.assertLess(remaining_after_resume, remaining_at_pause)
        timer.stop()

    def test_timer_zero(self):
        """Test zeroing timer sets remaining to 0."""
        timer = Timer(duration=10.0)
        timer.start()
        time.sleep(0.2)
        timer.zero()
        self.assertEqual(timer.get_remaining_time(), 0.0)

    def test_timer_restart(self):
        """Test restart resets timer to original duration."""
        timer = Timer(duration=5.0)
        timer.start()
        time.sleep(1.0)
        timer.restart()
        remaining = timer.get_remaining_time()
        self.assertGreater(remaining, 4.5)
        timer.stop()

    def test_timer_update_duration(self):
        """Test updating timer duration."""
        timer = Timer(duration=10.0)
        timer.update_duration(30.0)
        self.assertEqual(timer.duration, 30.0)
        self.assertEqual(timer.remaining, 30.0)

    def test_timer_set_goal(self):
        """Test setting goal dynamically."""
        timer = Timer(duration=5.0)
        timer.set_goal("New goal")
        self.assertEqual(timer.goal, "New goal")

    def test_timer_format_remaining_time(self):
        """Test timer formats remaining time correctly."""
        timer = Timer(duration=125.0, goal="Test")
        remaining_str = timer.get_remaining_time_str()
        self.assertIn("02:05", remaining_str)
        self.assertIn("Goal: Test", remaining_str)

    def test_timer_silent_mode(self):
        """Test silent mode toggle."""
        timer = Timer(duration=5.0)
        self.assertFalse(timer.is_silent())
        timer.toggle_silent()
        self.assertTrue(timer.is_silent())
        timer.toggle_silent()
        self.assertFalse(timer.is_silent())


if __name__ == "__main__":
    unittest.main()
