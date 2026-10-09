---
name: security
description: Security patterns for Elixir/Phoenix apps. Input validation, auth, injection prevention, upload safety, and production hardening. Use when reviewing for security or implementing auth flows.
---

# Security

## Input Validation

- **Never use `String.to_atom/1` on user input.** Atom table is finite, never GC'd. Use a whitelist `case` or `String.to_existing_atom/1`.
- **Never interpolate user input into `fragment()` or raw SQL.** Use `^value` in Ecto queries, `?` in fragments, `$1` in raw SQL.
- **Never render user content with `raw/1` in HEEx.** Let auto-escaping run. Sanitize with `HtmlSanitizeEx` and an explicit tag allowlist if HTML rendering is required.
- **Treat all LiveView event params as untrusted.** Users can alter forms and `phx-value-*` in DevTools. Validate with a changeset.
- **Authorize in EVERY `handle_event`.** Don't trust that `mount` authorized the action. Socket state can be stale.
- **Null bytes crash Postgres** (valid UTF-8 but rejected by PG). Sanitize at boundaries: `String.replace(input, "\x00", "")`.

## Authentication

- **Timing-safe comparison:** `Plug.Crypto.secure_compare/2` for tokens, never `==` (leaks via timing).
- **Timing-safe auth:** `Argon2.no_user_verify()` when no user found to prevent user enumeration.
- **Upload `content_type` is user-provided.** Always validate actual file contents (magic bytes) AND extension. Rewrite filename with `Ecto.UUID.generate()`.
- **Read webhook body BEFORE `Plug.Parsers`** for signature verification. Don't use `preserve_req_body: true` (keeps body in memory for ALL requests).
- **Sensitive data redaction:** `field :hashed_password, :string, redact: true`, `@derive {Inspect, except: [:password_hash]}`, `config :phoenix, :filter_parameters`.

## CSRF and CSP

- **Never disable Phoenix CSRF protection.** Use `<.form>`, not raw `<form>` tags. API pipelines use Bearer tokens instead.
- **Implement Content-Security-Policy** via `put_secure_browser_headers`. Account for LiveView WebSocket connections.

## Authorization

- **Scoped queries are the strongest authorization:** `where(user_id: ^user.id)` means no separate check needed.
- **Policy modules for complex permissions:**

```elixir
defmodule MyApp.Policy do
  def authorize(%User{role: :admin}, _action, _resource), do: :ok
  def authorize(%User{id: id}, :read, %Order{user_id: id}), do: :ok
  def authorize(_, _, _), do: {:error, :unauthorized}
end
```

- **Server-side authorization in event handlers.** UI hiding is not security.
- **Test both authorized AND unauthorized paths** for every mutating operation.

## File Uploads

- **Validate extension AND magic bytes.** Without magic byte validation, attackers upload HTML as `.jpg` for XSS.
- **Generate unique filenames** with `Ecto.UUID.generate()` to prevent collisions and path traversal.
- **`priv/static/uploads` is dev-only.** In releases, `priv/static` is replaced on every deploy. Use object storage or a mounted volume.
- **Set `x-content-type-options: nosniff` header** when serving uploaded files.
- **Use `Path.safe_relative/2`** for user-provided file paths.

## Production Hardening

- **Database URL uses TLS/SSL.** Never skip `verify: :verify_peer`.
- **Cookies: `secure: true` and `http_only: true`.**
- **`:info` log level in production.** `:debug` logs SQL query parameters including PII. Allow override via `LOG_LEVEL` env var.
- **Never log passwords, tokens, or PII.** Log identifiers only.
- **SSRF prevention:** block internal IPs (127.0.0.0/8, 10.0.0.0/8, 169.254.169.254). URL allowlist for webhooks.
- **Safe deserialization:** `Plug.Crypto.non_executable_binary_to_term/1` instead of `:erlang.binary_to_term`.
- **CORS: explicit origin allowlist.** Never regex that matches substrings (`~r/.*example\.com/` matches `evil-example.com`).

## Rate Limiting

- **Rate limit login attempts** (via Hammer or Oban).
- **Composite key strategy:** rate limit on multiple dimensions (IP AND email for magic links, user AND IP for API).
- **Rate-limited intake** for agent-filed reports (20/day per user).

## Dependency Auditing

Run before every merge:
```bash
mix hex.audit        # retired packages
mix deps.audit       # known CVEs (mix_audit)
mix sobelow          # static analysis
```

Each ignored advisory ID must have a comment naming the GHSA and the condition that re-enables the check.
