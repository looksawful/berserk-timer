from src import Timer


def test_toggle_silent():
    timer = Timer(10)
    # By default, silent mode should be off
    assert not timer.is_silent()
    timer.toggle_silent()
    # After the first toggle, silent mode should be enabled
    assert timer.is_silent()
    timer.toggle_silent()
    # After the second toggle, silent mode should be disabled
    assert not timer.is_silent()
