# Release and quality gate

Use this skill before a release, install-flow change, dependency update, README compatibility claim, or merge that changes user-visible behavior.

## Evidence gate

Collect evidence instead of inferring support:

1. `python -m compileall -q src`
2. `python -m pytest -q`
3. `ruff check src tests`
4. `mypy src`
5. `pip-audit -r requirements.txt`
6. direct CLI smoke test for help and at least one short timer path;
7. platform smoke evidence for every platform claimed as supported.

Existing Ruff/MyPy debt may remain advisory while it is being paid down, but new findings caused by the change should not be added casually.

## Release consistency

Verify that these agree before publishing:

- `src/version.py`;
- README version and What's New section;
- CHANGELOG;
- config keys/defaults;
- launcher names and commands;
- actual CLI flags/help;
- supported-platform claims;
- dependency/license notes.

## Dependency hygiene

Keep runtime dependencies separate from testing/linting/security tools. Prefer constrained development-tool versions for reproducible CI. Record dependency-audit findings as issues rather than silently suppressing them.

## Packaging direction

`setup.py` should not masquerade as packaging metadata if it is only a bootstrap script. The target is modern `pyproject.toml` packaging with a console entry point such as `berserk`, while preserving `python -m src.main` during migration.

## Do not

- declare Linux/macOS supported from a headless import/test run alone;
- merge broad formatter/autofix churn with a behavioral release fix;
- publish README commands that have not been executed against the branch;
- treat advisory static checks as proof that behavioral tests passed, or vice versa.
