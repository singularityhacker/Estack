# Contributing

A useful change prevents a concrete failure or makes an existing workflow easier to execute. Keep project preferences distinguishable from correctness requirements.

## Before editing

Read `AGENTS.md`, the affected skill, and its sources. Check dependency/client versions before recommending APIs or installation paths. Preserve attribution for adapted material. Keep each skill independently understandable and reference bundled resources by relative links.

## Local checks

Python 3.10+ is enough for package checks:

```bash
python3 scripts/catalog.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

With Node.js 22.20.0+ and npm, verify installer behavior in temporary projects:

```bash
DISABLE_TELEMETRY=1 python3 scripts/test_install.py
```

For the custom Credo check and Elixir examples, use the validation-only Mix fixture:

```bash
cd tests/quality_fixture
mix deps.get
mix format --check-formatted
mix test
```

CI uses Elixir 1.18.4 / OTP 27.3. The fixture is a test harness for bundled helpers, not a Phoenix starter app or an agent benchmark. No paid API credentials, database, or vendor services are required.

## Skill changes

Use unique `estack-` names matching directory names and concise frontmatter descriptions. Keep metadata compatible with the Agent Skills format. After a rename/addition, regenerate the README catalog and update the skill count, router, relevant installation notes, and changelog.

For code/config examples, state prerequisites and whether the example is complete or a fragment. Add focused regression tests for executable helper behavior. Do not add tests that merely restate an implementation detail.

Keep the Cursor and Claude manifests on the same version and canonical repository URL. Separate observed validation from intended compatibility. Do not add a tested badge for an editor you have not actually exercised.

## Reports and PRs

Include the problem, affected versions, changed behavior, and checks actually run. For a rule correction, link the relevant upstream documentation and describe why the former wording could mislead an agent. Keep unrelated changes separate.
