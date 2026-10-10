---
name: estack-ecto
description: Implement Ecto data access, ownership, changesets, transactions, and safe migrations. Use when editing schemas, queries, tenant-scoped contexts, or database writes.
---

# Ecto patterns

Read the project's Repo, auth scope, schemas, database adapter, and installed Ecto version. If the app uses Ash resources, use its actions and policies rather than bypassing them with Repo calls.

## Ownership and action authorization

Accept the existing authenticated scope at the context boundary. Cast only client-editable fields; set ownership from trusted identity. The following is an illustrative context fragment; `Scope`, `Report`, `Policy`, and `Repo` are application modules:

```elixir
def create_report(%Scope{user: user} = scope, attrs) do
  with :ok <- Policy.authorize(scope, :create_report) do
    %Report{user_id: user.id}
    |> Report.create_changeset(attrs)
    |> Repo.insert()
  end
end
```

In `create_changeset`, omit `:user_id`, `:tenant_id`, roles, and other protected fields from `cast`. Do not atomize arbitrary client keys. Use action-specific changesets so update input cannot change ownership. Keep caller parameters consistently string-keyed or atom-keyed as required by Ecto; do not mix them while stamping ownership.

## Scope every operation

```elixir
# Illustrative owner-only lookup using the project's Scope struct.
def get_report(%Scope{user: %{id: user_id}}, id) do
  case Repo.one(from r in Report, where: r.user_id == ^user_id and r.id == ^id) do
    nil -> {:error, :not_found}
    report -> {:ok, report}
  end
end
```

Scope reads, updates, deletes, aggregates, preloads, and background work. For organizations, scope to authorized membership and the selected tenant; a user ID alone is not a tenancy model. Avoid blanket admin bypasses unless the product's policy explicitly grants that access.

Authorize the requested action as well as resource visibility. Use scoped lookups on writes, and consider constraints or locking when authorization or state may change concurrently. Return `:not_found` for resources whose existence must be hidden; preserve deliberate `:forbidden` semantics for visible resources with disallowed actions.

Test with two users in different tenants, plus same-tenant users with different permissions. Test mutations as well as lists.

## Data integrity

- Use database constraints for uniqueness and references, with corresponding changeset constraints for useful errors. Validation alone cannot prevent races.
- Use integers in documented minor units or Decimal for money; preserve currency and rounding rules. Introduce custom Ecto types when they enforce a useful domain invariant.
- Validate addresses and other domain identifiers explicitly. A custom type is an option, not a requirement for every string field.
- Use UTC timestamps for instants, preserving the project's precision (`:utc_datetime` or `:utc_datetime_usec`). NaiveDateTime has no timezone; its correctness depends on the application's explicit convention.
- Bound pagination and filter inputs. Preload what the caller needs and inspect N+1 queries.

## Transactions and external effects

Group dependent writes in a transaction. This illustrative fragment assumes Oban uses the same Repo/database:

```elixir
Ecto.Multi.new()
|> Ecto.Multi.insert(:order, order_changeset)
|> Oban.insert(:sync_job, fn %{order: order} ->
  SyncJob.new(%{order_id: order.id})
end)
|> Repo.transaction()
```

Match the Multi result, including `{:error, step, reason, changes_so_far}`. Test that failed steps roll back both the domain write and queued job. Prefer the transaction API supported by the locked Ecto version; `Repo.transaction/1` is shown for compatibility.

Do not make an irreversible vendor request inside a database transaction and assume rollback undoes it. Persist intent/outbox work and make external effects idempotent. Choose optimistic or pessimistic locking based on the contested invariant.

## Migrations

Generate migrations with `mix ecto.gen.migration`. Never edit an already-applied migration as a shortcut. Distinguish writing/reviewing a migration from executing it against production; use the authorization provided for the task.

Use expand/backfill/contract for rolling deployments. Consider table locks, concurrent indexes, database support, nullable transitions, and old application versions. Run the project's migration checker if installed. Scope and justify exceptions using the installed checker's syntax; a suppression comment does not make a change safe.

Keep seeds idempotent. Separate optional development sample data from production bootstrap operations and never require vendor credentials for ordinary tests.

## References

- [Ecto.Multi](https://hexdocs.pm/ecto/Ecto.Multi.html)
- [Ecto.Changeset](https://hexdocs.pm/ecto/Ecto.Changeset.html)
- [Phoenix scopes](https://hexdocs.pm/phoenix/scopes.html)
