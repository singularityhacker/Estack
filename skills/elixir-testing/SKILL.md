---
name: elixir-testing
description: Testing patterns for Elixir/Phoenix apps. Fixtures, fakes, isolation, property tests, and LiveView testing. Use when writing tests or setting up test infrastructure.
---

# Elixir Testing

## Tests need Postgres and nothing else

No `.env` file. No vendor credentials. `config/runtime.exs` skips third-party credentials when `config_env() == :test`.

**Rule:** Do not add a test that needs a real API key. If a behavior depends on a vendor, swap the implementation.

## Vendors are behaviours with a Fake

```elixir
# lib/my_app/github.ex
defp impl do
  Application.get_env(:my_app, :github_impl, MyApp.GitHub.Client)
end

# config/test.exs
config :my_app, :github_impl, MyApp.GitHub.Fake
```

The Fake is a real implementation returning deterministic `{:ok, _}` / `{:error, _}`. Dev without credentials uses it too.

**Rule:** Do not stub with Mox unless the call site already uses it. Add a Fake and a config key.

## Fixtures call the real context

```elixir
def user_fixture(attrs \\ %{}) do
  {:ok, user} =
    attrs
    |> Enum.into(%{email: unique_email()})
    |> Accounts.register_user()

  confirm_user(user)
end
```

A fixture that `Repo.insert!`s a half-valid user skips the changeset the production path runs. The test passes on data the app cannot create.

**Rule:** Build test rows by calling the context function. Use `Repo.insert` directly only when testing a raw constraint.

## Two users, and the second gets :not_found

For every new read or write that takes an id:

```elixir
test "other user cannot access" do
  owner = user_fixture()
  other = user_fixture()
  {:ok, report} = Feedback.create_report(owner, valid_attrs())

  assert {:error, :not_found} = Feedback.get_report(other, report.public_id)
end
```

Return `:not_found`, not `:forbidden`. `:forbidden` tells the caller the row exists.

## Async is the default you earn

```elixir
use MyApp.DataCase, async: true
```

Drop `async: true` when the test mutates global application env or a named process. Do not call `Process.sleep`. Wait with `Process.monitor` or `:sys.get_state/1`.

## Oban does not run in tests

```elixir
# config/test.exs
config :my_app, Oban, testing: :manual
```

Assert on the job args you enqueued. Drain with `Oban.drain_queue` or `perform_job` in the test that owns the worker. Do not turn testing back to `:inline` globally.

## LiveView tests target DOM ids

```elixir
assert has_element?(view, "#order-form")
view |> form("#order-form", order: %{title: "Test"}) |> render_submit()
assert has_element?(view, "#order-item-1")
```

Put a stable `id` on the form, button, or region you need to test. Do not match raw HTML strings for behavior.

## Coverage

- Set a project-wide floor with `floor_coverage: true`.
- Critical paths get higher per-file thresholds.
- Add tests for the branch you touched.
- Do not add your module to `skip_files` to go green.

## Property tests for state machines

When a module declares phases, statuses, or allowed transitions:

```elixir
property "every declared terminal phase is terminal" do
  check all phase <- member_of(Transitions.terminal_phases()) do
    assert Transitions.terminal?(phase)
  end
end
```

Keep DB-backed properties `async: false`. Do not reach for StreamData for ordinary CRUD tests.

## HTTP testing

- Use `Bypass` when asserting on the request path or status the HTTP client parses.
- `Bypass` tests are `async: false`.
- For everything else, use the Fake.

## No browser end-to-end

Do not add Wallaby, Playwright, or a browser CI job. Cover the LiveView with `Phoenix.LiveViewTest`.
