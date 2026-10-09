---
name: elixir-idioms
description: Elixir language patterns, control flow, error handling, and idioms. Use when writing Elixir code or reviewing for idiomatic style.
---

# Elixir Idioms

## Control Flow

**Pattern match on function heads, not if/else in bodies:**

```elixir
# Good
def process(%{role: :admin} = user), do: admin_path(user)
def process(%{role: :member} = user), do: member_path(user)

# Bad
def process(user) do
  if user.role == :admin, do: admin_path(user), else: member_path(user)
end
```

**`with` for 2+ sequential fallible operations:**

```elixir
with {:ok, user} <- Accounts.get_user(id),
     {:ok, order} <- Orders.create(user, params) do
  {:ok, order}
else
  {:error, :not_found} -> {:error, :user_not_found}
  {:error, changeset} -> {:error, changeset}
end
```

**Never nest `case` statements.** Refactor to `with`, separate functions, or multi-clause function heads.

## Error Handling

**Tagged tuples for all fallible public functions:** `{:ok, result} | {:error, reason}`

**Let it crash under supervisors:** handle expected errors explicitly. Let unexpected errors crash so supervisors restart. "Let it crash" means "let it heal," not "write careless code."

**`rescue` only for external library code.** Never rescue for control flow. Every rescue must list exact exception types:

```elixir
# Good
rescue
  e in [Jason.DecodeError, Mint.TransportError] -> {:error, e}

# Bad -- swallows KeyError, CompileError, everything
rescue
  _ -> {:error, :unknown}
```

Never include programmer-bug exceptions (`UndefinedFunctionError`, `CompileError`, `BadArityError`) in rescue lists. Use `reraise e, __STACKTRACE__`, never `reraise e, []`.

**`try/after` for resource cleanup, not `try/rescue`:**

```elixir
try do
  File.open!(path)
  # ... work ...
after
  File.close(file)
end
```

## Guards

- Use `and`/`or`/`not` in guards, never `&&`/`||` (guards require boolean operands).
- `%{}` matches ANY map -- use `map_size(map) == 0` guard for empty maps.
- `is_non_struct_map/1` (Elixir 1.17+) distinguishes plain maps from structs.
- Reserve `is_thing` names for guard functions only.

## Data Modeling

**Structs over maps when shape is known.** Use tagged tuples + pattern matching for polymorphism instead of class hierarchies.

**Assertive map access:** use `.key` (raises `KeyError`) for required keys. Use `[:key]` only for truly optional keys.

**Pattern match over boolean obsession:** `%{role: :admin}` not `%{is_admin: true}`.

## Polymorphism Decision Ladder

1. Pattern matching (simplest)
2. Anonymous functions
3. Behaviours (module polymorphism, very cheap at runtime)
4. Protocols (composing data types, especially built-ins)
5. Message passing (only when stateful by design)

Only reach for polymorphism when justified. Single implementation = stay coupled.

## Performance Idioms

- **Prepend to lists:** `[new | list]` not `list ++ [new]`
- **Stream for large collections** with multiple transformations; Enum for small/medium
- **`tap/1` for side effects, `then/1` for transformations** in pipes
- **Start pipes with data:** `id |> get_user() |> process()` not `get_user(id) |> process()`
- **Small sub-binary keeps large parent alive:** use `:binary.copy(small)` when keeping only a small slice

## Modern Elixir

- **Built-in `JSON` module** (Elixir 1.18+) instead of Jason
- **`Duration` module** (Elixir 1.18+): `Duration.new!(hour: 2)` instead of magic numbers
- **`unless` deprecated** (Elixir 1.18+): formatter rewrites to `if !condition`
- **Gradual type checker** (Elixir 1.20): built into `mix compile`, reports verified bugs as warnings

## Wrapping Third-Party Libraries

Facade external deps behind project-owned modules. Enables swapping without touching callers:

```elixir
# Good: your module wraps the library
defmodule MyApp.Mailer do
  def send(email), do: Swoosh.deliver(email)
end

# Bad: library called directly everywhere
Swoosh.deliver(email)  # in controller
Swoosh.deliver(email)  # in worker
Swoosh.deliver(email)  # in context
```

## Testing Idioms

- **Pattern-match assertions:** `assert [%{name: "Alice"}] = students` not `assert length(students) == 1`
- **`@tag :tmp_dir`** for async-safe file tests
- **`assert_receive` with timeout:** `assert_receive {:done, _}, 5_000` not `Process.sleep(1_000)`
- **Test your code, not the framework:** if deleting your code doesn't fail the test, it's tautological
- **`unbuffer` prefix for mix commands in agents** to prevent stdout block-buffering in non-TTY environments
