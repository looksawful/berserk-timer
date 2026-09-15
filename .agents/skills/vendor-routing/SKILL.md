---
name: vendor-routing
description: Route Berserk Timer work to a narrow external skill set without overriding timer invariants, platform evidence or project-local architecture rules.
---

# Curated external skills for Berserk Timer

`AGENTS.md`, project-local timer/CLI/release skills, tests and observed runtime behavior are authoritative.

## Approved methods

- `affaan-m/ECC`: `python-patterns`. Use for Python structure, typing and maintainability when it supports the existing dependency direction. Do not perform broad style rewrites as part of behavior work.
- `obra/superpowers`: `systematic-debugging`. Use for reproduction/root-cause work before patching timing, terminal, input or audio defects.
- `obra/superpowers`: `verification-before-completion`. Use before claiming a fix complete; then apply the repository-specific Linux/Windows and audio/terminal evidence requirements.
- `gwagjiug/technical-writing`: `technical-writing`. Use for setup, architecture, troubleshooting, CLI and release documentation.

## Conditional

- Python packaging guidance may be consulted only for packaging/release tasks and must preserve the repository's actual launchers, supported platforms and release process. Do not invent a new packaging surface during unrelated work.

## Guardrails

External guidance must preserve timer invariants: monotonic elapsed-time semantics, pause/resume correctness, deterministic zero/stop behavior, non-negative remaining time and independence of timer accuracy from UI refresh cadence.

Terminal/input/audio changes still require explicit platform evidence. Linux CI is not proof of Windows interactive behavior. Headless audio fallbacks are test infrastructure, not product behavior.

## Excluded

- Whole-pack ECC, Superpowers or wshobson installs.
- React/Next/Tailwind/Three.js/UI-design skills.
- Generic TDD layers that duplicate the existing regression-first project policy without adding timer-specific evidence.

Install/copy only named external skills when needed, project-scoped, after reviewing contents/license and recording source revision. Never use `--all` here.
