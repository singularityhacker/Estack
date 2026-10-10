# Estack maintenance

Estack distributes agent instructions and optional development helpers. It is not itself a Phoenix application.

- Read the task and existing authorization. Use branches/PRs by default; honor explicit authorization for direct pushes when repository controls permit them.
- Keep framework invariants separate from project preferences. Preserve daisyUI, Mox/fakes, existing toolchains, and app architecture where chosen.
- Check installed/versioned primary documentation before changing technical claims.
- Keep skills portable and self-contained. Bundle required resources inside their skill directory and avoid relying on a repo-root file after installation.
- Namespace skills with `estack-` and update the router/catalog for additions or renames.
- Run `python3 scripts/catalog.py`, `python3 scripts/validate.py`, and the Python tests after package edits. Run the relevant Mix fixture and installer smoke tests for executable changes.
- Record enhancements in CHANGELOG.md and keep compatibility/validation claims factual.
- Do not claim runtime/editor testing from a successful metadata check. Never weaken a failing check solely to obtain green CI.
