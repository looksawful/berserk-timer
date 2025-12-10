import pytest

import src.main as main


def test_cleanup_screen_exists():
    assert hasattr(main, "cleanup_screen")


def test_stop_sound_exists():
    assert hasattr(main, "stop_sound")
