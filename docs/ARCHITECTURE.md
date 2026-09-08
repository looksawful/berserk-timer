# Berserk Timer architecture

## Current runtime map

The current CLI entry point is `src.main`.

```text
brsrk.bat / brsrk.sh
        |
        v
src.main
  |-- argument parsing / interactive prompts
  |-- config loading
  |-- timer lifecycle orchestration
  |-- witness flow orchestration
  |-- repeating alarm thread
  |
  +--> src.timer.Timer
  +--> src.cli
  +--> src.logger
  +--> src.screen_manager

src.cli
  |-- Rich rendering
  |-- keyboard polling (msvcrt / termios + select)
  |-- timer command handlers
  |-- log viewing/deletion
  |-- audio-settings UI and preview control
  +--> Timer, logger/audio functions, screen manager

src.logger
  |-- application/system logging
  |-- witness log filesystem I/O
  |-- sound lookup/playback
  +-- platform-specific audio subprocess/pygame behavior
```

`Timer` is the active engine. The repository currently contains no `TimerCore` implementation even though README text refers to one.

## What is already healthy

- Timer state has a dedicated class rather than living entirely in the UI loop.
- Duration validation and several state transitions have automated tests.
- Windows and POSIX keyboard paths are at least separated at function-definition level.
- Screen cleanup is centralized in `screen_manager`.
- Config loading and logging are separate modules.

## Main architecture risks

### 1. Timer elapsed time uses wall clock

`Timer._run()` measures elapsed duration with `time.time()`. Timer duration should use a monotonic source so system clock corrections cannot change elapsed-time semantics. UI refresh must remain independent of timer accuracy.

### 2. `main.py` is both composition root and application service

`main.py` currently owns parsing, interactive input, duration selection, goal input, timer creation, restart loops, witness orchestration and repeating alarm behavior. This makes application workflows hard to test without terminal I/O.

### 3. `cli.py` is a large coupled adapter

`run_cli_timer()` contains nested command handlers while the module also owns Rich rendering, raw keyboard access, screen navigation, logging actions and audio settings. Input, rendering and application commands cannot be tested independently with small fakes.

### 4. `logger.py` mixes unrelated infrastructure

Logging, witness-file persistence and audio playback live together. These have different failure modes and platform requirements. A future split should preserve behavior while giving each responsibility a small API.

### 5. Configuration location depends on current working directory

`load_config()` defaults to `config.json` in the process CWD and creates it when missing. Launching from another directory can therefore read/create a different config. The desired user-config location and migration contract must be defined before changing this behavior.

### 6. Launcher behavior is not a transparent adapter

The Windows launcher hard-codes one global Python installation when no local venv exists and injects witness mode. The POSIX launcher injects both a five-minute duration and witness mode before forwarding arguments. Wrappers should select an interpreter and forward the user's command, not silently redefine it.

### 7. Packaging/bootstrap contract is unclear

`setup.py` is a venv/bootstrap helper, not package metadata. Its attempt to run a virtual-environment activation script in a subprocess cannot activate the caller process. Runtime and test dependencies also share `requirements.txt`.

## Target dependency direction

A behavior-preserving refactor should converge on:

```text
                 CLI entry / composition root
                           |
                           v
                 application/session service
                  /         |          \
                 v          v           v
          timer domain   witness port   alarm port
              |              |             |
              |              v             v
              |         terminal UI     audio adapter
              |                            |
              +----------------------------+
                         no reverse imports

infrastructure: config repository, witness log repository,
platform keyboard adapter, screen adapter, audio backend
```

The important rule is dependency direction, not a folder-count ceremony. The timer core should know nothing about Rich, pygame, terminal raw mode, filesystem paths or witness prompts.

## Safe refactor sequence

1. Freeze current behavior with CLI/main/screen tests and launcher smoke contracts.
2. Correct documentation/launcher inconsistencies independently.
3. Introduce an injectable monotonic clock into timer semantics and preserve public behavior.
4. Extract application/session orchestration from `main.py` without changing text or UX.
5. Extract CLI input/rendering adapters from command execution.
6. Separate audio and witness-log persistence from `logger.py`.
7. Introduce real `pyproject.toml` packaging and a console entry point after runtime boundaries are stable.

Each step should remain independently reviewable and should not include broad formatting churn.
