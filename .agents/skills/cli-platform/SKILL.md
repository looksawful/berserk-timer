# CLI and platform adapters

Use this skill when changing argument parsing, launchers, keyboard input, terminal screen behavior, witness prompts, audio selection/playback, or OS-specific code.

## Goal

Keep the CLI predictable and make platform assumptions explicit instead of silently baking one developer machine into the product.

## Workflow

1. Identify whether the change is argument semantics, terminal I/O, screen lifecycle, audio, or launcher behavior.
2. Preserve user arguments exactly. A launcher may choose an interpreter, but it must not silently inject duration, witness mode, or other behavior.
3. Prefer `sys.executable`, an active virtual environment, `py`, or `python`/`python3` discovery over fixed installation paths.
4. Keep Windows and POSIX implementations behind the same small interface where practical.
5. For headless automated tests, use dummy audio and mocked terminal input rather than weakening runtime behavior.
6. Run the full pytest suite. For Windows-specific changes, record a Windows smoke test separately because Linux CI cannot prove `msvcrt`, console-buffer, shortcut, or Windows audio behavior.

## Contracts

- `python -m src.main <args>` remains the canonical direct invocation until real packaging is introduced;
- launcher arguments are forwarded once, in order;
- help text and README name only files/options that exist;
- alternate-screen cleanup happens on normal exit and exceptional exit paths;
- keyboard listeners terminate cleanly;
- preview audio cannot outlive or override the real timer alarm;
- platform fallbacks fail clearly and do not hang startup.

## Avoid

- hard-coded absolute interpreter paths;
- implicit default duration inside shell/batch wrappers;
- assuming successful import on Ubuntu means interactive Linux/macOS support is proven;
- placing more OS branches inside domain timer logic.
