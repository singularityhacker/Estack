---
name: elixir-tdd
description: Test-driven development for Elixir. Write the failing test first, then the fix. Use when fixing bugs or building features test-first.
---

# Elixir TDD

## The loop

1. **Red.** Write a test that fails for the right reason. Run it. Confirm it fails.
2. **Green.** Write the smallest change that makes it pass. Run it. Confirm it passes.
3. **Repeat.** Next test, next behavior.

Do not write multiple tests before any implementation. One test, one pass, then the next.

## Where to test

Test at the context boundary. Call the public function the way its callers do:

```elixir
# Good: tests the context API
test "create_order/2 validates required fields" do
  user = user_fixture()
  assert {:error, changeset} = Orders.create_order(user, %{})
  assert %{title: ["can't be blank"]} = errors_on(changeset)
end

# Bad: tests internal implementation
test "Order.changeset/2 sets default status" do
  # This couples the test to the schema internals
end
```

## Anti-patterns to avoid

| Anti-pattern | The tell |
|---|---|
| Implementation-coupled | Test breaks when you rename an internal function |
| Tautological | Expected value is computed the same way the code computes it |
| Horizontal slicing | All tests first, then all implementation |

## Mocking rules

- Vendors are Fakes selected by config (see `/elixir-testing`).
- Use Bypass when asserting on the raw HTTP request.
- Do not mock your own contexts. Call the real function.
- Do not mock Ecto or Repo. Use the sandbox.

## Bug fix workflow

1. Read the bug report. Understand the symptom.
2. Write a test that reproduces the bug. Run it. Confirm it goes red.
3. Fix the bug. Run the test. Confirm it goes green.
4. Run the full test file. Then run `mix verify`.
5. The test is the regression guard. Do not delete it.

## When to skip TDD

Some changes have no good test target:

- Config changes, wiring, environment variables
- Pure template/CSS changes with no logic
- Dependency upgrades (the existing suite is the test)

For these, run the existing suite and verify manually. Do not force a test where none adds value.
