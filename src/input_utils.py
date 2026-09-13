def read_input(prompt: str = "") -> str | None:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return None
