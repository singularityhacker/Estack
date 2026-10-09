---
name: ecto-patterns
description: Ecto schema, changeset, query, migration, and transaction patterns for Phoenix apps. Use when working with the database layer, writing migrations, or structuring data access.
---

# Ecto Patterns

## Ownership stamping

The context stamps ownership. The changeset validates shape.

```elixir
def create_report(%User{} = user, attrs) do
  params =
    attrs
    |> atomize_create_attrs()
    |> Map.put(:user_id, user.id)
    |> Map.put_new(:public_id, generate_public_id())

  %Report{}
  |> Report.create_changeset(params)
  |> Repo.insert()
end
```

**Rule:** Take the user as the first argument of any function that reads or writes their data. Set `user_id` from the authenticated user, not from client input. Split changesets by action (`create_changeset` vs `update_changeset`) so a caller cannot set fields they should not control.

## Query scoping

Scope to the viewer before any filter:

```elixir
def list_reports(%User{} = user, opts \\ []) do
  Report
  |> scope_to_viewer(user)
  |> apply_filters(opts)
  |> limit(^clamp_limit(opts))
  |> Repo.all()
end

defp scope_to_viewer(query, %User{is_admin: true}), do: query
defp scope_to_viewer(query, %User{id: id}), do: where(query, user_id: ^id)
```

**Rule:** Write a test with two users. Assert the second user's row is absent. Return `{:error, :not_found}` for a row the caller cannot see -- do not reveal that it exists. Clamp limits (e.g., max 100) so an unbounded `Repo.all` cannot DoS your database.

## Timestamps

```elixir
timestamps(type: :utc_datetime)
```

Always. Naive datetimes make "last 24 hours" and cron windows wrong twice a year.

## Custom types for money and addresses

Do not use `:float` for money. Do not use `:string` for wallet addresses.

```elixir
field :amount, MyApp.Types.USDCAmount
field :wallet, MyApp.Types.EVMAddress
```

The type module implements `Ecto.Type` and rejects bad input at the changeset. A plain `:string` wallet column will store `"0xDEAD"`. The type fails the write.

## Transactions with Ecto.Multi

When one user action writes more than one row and later steps depend on earlier ones:

```elixir
Ecto.Multi.new()
|> Ecto.Multi.insert(:order, order_changeset)
|> Ecto.Multi.update(:quote, fn %{order: order} -> quote_changeset(order) end)
|> Ecto.Multi.run(:enqueue, fn _repo, %{order: order} ->
  Oban.insert(SyncJob.new(%{order_id: order.id}))
end)
|> Repo.transaction()
```

**Rule:** Test the rollback. Do not insert, then update, then enqueue as three separate Repo calls.

## Migrations

- Generate with `mix ecto.gen.migration`.
- Keep them additive when possible.
- Use `excellent_migrations` to check safety. Dangerous changes need a safety comment:

```elixir
# excellent_migrations:safety-assured-for-this-file column_removed
```

- Do not widen `skip_checks`. Name the exception.
- Money paths and migrations are human-authored. Agents investigate and report. Do not patch these paths unless the human asked for the change.

## Seeds

- Gate on an env var: `ADMIN_SEED_EMAIL`. Empty or missing, skip.
- Keep seeds idempotent.
- Do not insert sample data that could run on a fresh production database.
- Do not require a `.env` for `mix test`.

## Financial data isolation

For user-visible balances and sensitive data, wrap with an ownership tag:

```elixir
defmodule MyApp.OwnedData do
  defstruct [:owner_id, :data]

  def tag(data, %User{id: id}), do: %__MODULE__{owner_id: id, data: data}

  def unwrap!(%__MODULE__{owner_id: id, data: data}, %User{id: id}), do: data
  def unwrap!(_, _), do: raise "DATA ISOLATION VIOLATION"
end
```

Tag in the context. Unwrap at the last step before render, passing the viewer.
