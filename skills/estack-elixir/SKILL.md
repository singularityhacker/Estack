---
name: estack-elixir
description: Write idiomatic, version-compatible Elixir and handle errors explicitly. Use when editing control flow, types, collections, resource handling, or library boundaries.
---

# Elixir idioms

Read the project's toolchain and formatter configuration. Use APIs supported by the installed Elixir/OTP versions; avoid blanket dependency replacements on the basis of newer standard-library features.

## Control flow and contracts

Use function heads and pattern matching when they clarify shape or distinct cases. Use `if` for simple boolean branches, `case` for alternatives, and `with` for sequential fallible operations. Avoid deeply nested branches, but do not turn every conditional into a new function.

Ensure a `with` failure identifies the failing operation when error shapes overlap. Preserve established public return contracts; expected fallible operations commonly return `{:ok, value}` or `{:error, reason}`. Bang functions are appropriate when failure should terminate the current operation.

Handle expected errors explicitly. Let unexpected process failures reach appropriate supervision; a restarted process does not restore in-memory state or undo external side effects.

## Exceptions and resources

Rescue only errors you can meaningfully handle, naming their types. Avoid broad rescues that convert programmer defects into success. Preserve stacktraces with `reraise error, __STACKTRACE__` when rethrowing.

Prefer resource-owning APIs. This complete function closes the file even if the callback raises:

```elixir
defmodule Estack.Examples.FileReader do
  def first_line(path) do
    File.open(path, [:read], fn file -> IO.read(file, :line) end)
  end
end
```

When using `try/after` directly, acquire and bind the resource before the `try` and release exactly that resource in `after`.

## Data and guards

- Use structs for a known domain shape and maps for flexible data.
- Use `.field` for required struct/map keys; use `Map.get` for optional map keys.
- Remember `%{}` matches any map. Check `map_size` for emptiness.
- Use guard-safe operations and `and`/`or`/`not` in guards. Ordinary predicate functions conventionally end in `?`; reserve `is_` names for guard-like predicates.
- Do not create atoms from untrusted runtime input. Prefer explicit string-key allowlists.
- Use behaviours for interchangeable implementations when the boundary is useful; do not wrap every library purely to speculate about replacement.

## Collections and performance

Prepend and reverse when constructing lists incrementally. Use Stream when laziness reduces work or memory, and Enum for straightforward bounded operations. Prefer clarity over blanket piping rules. Copy a small sub-binary only when retaining the parent causes a measured memory problem.

Use `tap/2` for side effects and `then/2` for transformations when they improve clarity and the project's Elixir version supports them.

## Version-sensitive choices

Check version-matched docs for `JSON`, `Duration`, compiler type analysis, and deprecated syntax before using them. Preserve the configured JSON encoder until protocol support and framework integrations have been checked. Do not remove Jason just because a standard-library JSON module is available.

Use the project's formatter settings rather than imposing a new line length. Use a PTY or supported runner option for output buffering problems; do not require the external `unbuffer` command on every machine.

## References

- [Elixir library guidelines](https://hexdocs.pm/elixir/library-guidelines.html)
- [File.open/3](https://hexdocs.pm/elixir/File.html#open/3)
