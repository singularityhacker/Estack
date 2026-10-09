---
name: investigate
description: Systematic bug investigation for Elixir/Phoenix apps. Reproduce first, fix second. Use when debugging or diagnosing a bug.
---

# Investigate

No fixes without investigation. No guessing.

## The loop

### 1. Collect symptoms

Read the bug report, error log, or Sentry issue. Note:
- What surface? (LiveView, API, MCP, Oban job, cron)
- What action triggered it?
- Is there a stacktrace?
- Is it reproducible or intermittent?

### 2. Read the code

Before forming a hypothesis, read the actual code path:
- The context function that handles the operation
- The changeset or validation logic
- The query scoping
- Recent changes to the file (`git log -5 <file>`)

### 3. Write a failing test

```elixir
test "reproduces the bug: order crashes on empty company" do
  user = user_fixture()
  # Replicate the exact conditions from the report
  assert {:error, _} = Orders.create_order(user, %{company: ""})
end
```

Run it. If it does not fail, your understanding of the bug is wrong. Go back to step 2.

### 4. Hypothesize

List 3-5 ranked hypotheses. The most common causes in Phoenix apps:

- Missing `where` clause (data from another user leaks through)
- Changeset not validating a field the form now sends
- `handle_event` pattern match doesn't cover the new case
- Oban job args changed but the worker pattern match didn't
- A context function returns `{:error, _}` but the caller pattern-matches only `{:ok, _}`

### 5. Fix

Write the smallest change that makes the test pass. Run the test. Then run the full test file. Then run `mix verify`.

### 6. Clean up

- Is the fix in the right layer? (Context, not LiveView. Changeset, not controller.)
- Did you handle both `{:ok, _}` and `{:error, _}`?
- Does the fix need a migration? If so, flag it for human review.

## Do not

- Do not fix code you haven't read.
- Do not fix unrelated code you noticed while investigating.
- Do not skip the failing test. If you can't reproduce, skip the item and say why.
- Do not edit money paths, migrations, or the gate without explicit approval.
