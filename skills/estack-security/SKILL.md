---
name: estack-security
description: Protect Phoenix authentication, authorization, uploads, webhooks, and input boundaries. Use when implementing access control, reviewing user input, exposing APIs/MCP tools, or hardening production configuration.
---

# Phoenix security

Read the installed framework versions and existing authentication/policy code. Preserve established mechanisms and assess the specific trust boundary; generic rules do not replace a threat model or security review.

## Inputs and authorization

- Treat LiveView params, hidden fields, `phx-value-*`, API payloads, and job inputs as untrusted.
- Derive ownership and tenant membership from authenticated server-side state. Do not cast client-supplied ownership, roles, or administrative flags.
- Scope data access and authorize the requested action. Being allowed to see a resource does not imply permission to edit, refund, or delete it.
- Check authorization at context/Ash-action boundaries for every transport. Recheck sensitive state during mutations; a previous mount check is not enough.
- Test unauthorized roles, different tenants, direct IDs, preloads, and writes. UI hiding and opaque IDs are not security controls.

## Injection and unsafe conversion

Use explicit allowlists for keys and tool names. Do not create atoms from untrusted strings; `String.to_existing_atom` alone is not an authorization allowlist and can still raise.

Bind values in Ecto/SQL queries. Allowlist dynamic identifiers, operators, and ordering separately; value binding does not sanitize SQL syntax. Let HEEx escape user content. Sanitize intentionally supported HTML with a maintained allowlist before rendering it as raw.

PostgreSQL text rejects NUL bytes; validate or reject them at the appropriate boundary rather than claiming the database server crashes. Do not silently alter signed webhook bodies or security-sensitive values before verification.

Avoid deserializing Erlang terms from untrusted sources. If a protocol truly requires it, use the installed library's safe decoding API, constrain input size/types, and validate the resulting schema. Safe decoding alone does not prevent resource exhaustion.

## Authentication and sessions

Prefer the existing Phoenix/auth-library implementation for session rotation, password checks, magic links, and sudo/re-auth flows. Use the library's timing-safe verification and no-user path where appropriate; do not invent a new token protocol.

Preserve CSRF protection for cookie-authenticated state changes, including APIs that use cookies. Configure secure/HttpOnly cookies, appropriate SameSite behavior, session expiry, and logout/revocation semantics. Bearer-token APIs need their own scope and storage decisions.

Use CSP compatible with the actual asset pipeline and LiveView connections. Treat CORS as a browser policy, not authentication.

## Uploads and paths

Set size/count/type limits. Check file signatures and parse/re-encode supported formats where appropriate; magic bytes and extensions alone do not prove a file is safe. Treat SVG/HTML and other active content specially. Generate storage names server-side and prevent traversal and unsafe extraction.

Serve untrusted uploads with deliberate content type, disposition, and `nosniff`, preferably from an isolated origin. Use durable object storage or a configured volume in production rather than assuming release directories persist.

## Webhooks and SSRF

Verify the exact raw body, signature, timestamp/replay window, and provider event identity. Configure a Plug body reader or route-specific parsing strategy compatible with the app; do not consume the body twice. Persist/deduplicate important events before acknowledging them.

For outbound user-selected URLs, prefer an allowlist. Validate schemes, hosts, resolved IPv4/IPv6 addresses, redirects, and each destination hop. Block loopback, private, link-local, metadata, and other disallowed networks, including DNS-rebinding paths. Apply timeouts, response-size limits, and egress controls where available.

## Operational controls

Filter credentials and sensitive params from logs, exceptions, traces, job args, and inspect output. Identifiers may also be sensitive; log only what operations require. Match TLS peer/hostname verification to the client and deployment's trust roots.

Rate-limit sensitive endpoints with a suitable request-rate limiter or gateway and use multiple dimensions where necessary. A background job queue is not a general login rate limiter.

Run the project's dependency audit and Sobelow configuration. Explain each accepted finding; do not silently widen skips. Classify MCP/API tools by actual read/write/admin capability and enforce access on the server, including unknown-tool denial.

## References

- [LiveView security](https://hexdocs.pm/phoenix_live_view/security-model.html)
- [Phoenix security guide](https://hexdocs.pm/phoenix/security.html)
