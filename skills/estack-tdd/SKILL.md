---
name: estack-tdd
description: Implement Elixir/Phoenix behavior through a red-green-refactor loop. Use for test-first features, regression fixes, and focused domain changes.
---

# Elixir TDD

Use the existing test framework and project conventions. Load `estack-testing` when sandbox, vendor isolation, or browser behavior is involved.

## Loop

1. Identify one observable behavior and its boundary.
2. Write the smallest useful failing test and run it. Confirm it fails for the intended reason, not missing setup.
3. Implement the behavior and run the test until it passes.
4. Refactor while keeping it green, then cover the next meaningful case.

Test public contexts/Ash actions by default. Test a pure function or changeset directly when that is the meaningful contract. Do not calculate expected results with the implementation under test.

## Bug fixes

Read the affected path and reproduce the symptom. Add a regression test when feasible, including the unauthorized/error case that actually failed. Run related tests and the available project gate before completion.

If reproduction is intermittent or environment-dependent, record evidence and limits; a test that happens to pass does not prove the diagnosis wrong. Use logs, traces, or controlled experiments. Do not invent a fix or claim a regression test passed without running it.

## Boundaries

Use the real database through the sandbox for persistence behavior. Use the project's existing vendor fake/mock/HTTP test boundary. Avoid mocking away the application behavior being asserted.

For configuration, dependency changes, prose, or purely visual changes, choose validation that can detect a real defect: compile, existing tests, config checks, or visual/browser review. Do not force a meaningless new unit test.
