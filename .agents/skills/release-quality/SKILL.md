# Release and quality gate

Use this skill before a release, install-flow change, dependency update, README compatibility claim, or merge that changes user-visible behavior.

## Evidence gate

Collect evidence instead of inferring support:

1. `python -m compileall -q src`
2. `python -m pytest -q`
3. `ruff check src tests`
4. `mypy src`
5. `pip-audit -r requirements.txt`
6. `python -m pip install .` followed by package import and `berserk --help` smoke checks;
7. installed-package verification for all five WAV alerts outside the source checkout;
8. platform smoke evidence for every platform claimed as supported.

Ruff and MyPy are enforced release gates. A release candidate is not clean while either reports findings.

## Release consistency

Verify that these agree before publishing:

- `src/version.py`;
- `pyproject.toml` package version;
- README version and release claims;
- CHANGELOG;
- config keys/defaults;
- launcher names and commands;
- actual CLI flags/help;
- supported-platform claims;
- dependency/license notes.

Also verify that release hardening did not accidentally modify the shipped ASCII artwork or WAV assets unless the release explicitly intends such a change.

## Dependency hygiene

Keep runtime dependencies separate from testing/linting/security tools. Prefer constrained development-tool versions for reproducible CI. Record dependency-audit findings as issues rather than silently suppressing them.

## Packaging

`pyproject.toml` is the packaging source of truth and provides the `berserk` console entry point. Preserve `python -m src.main` as the direct source invocation. Package smoke tests must run from outside the repository when checking installed data so the checkout cannot mask missing package assets.

## Do not

- declare Linux/macOS supported from a headless import/test run alone;
- merge broad formatter/autofix churn with a behavioral release fix;
- publish README commands that have not been executed against the branch;
- treat static checks as proof that behavioral tests passed, or vice versa;
- publish a release before a fresh full CI run passes on the exact release-candidate SHA and again on the merged `dev` SHA.
