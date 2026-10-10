---
name: estack-liveview
description: Build Phoenix LiveView forms, streams, components, hooks, and authenticated screens. Use when editing HEEx, LiveView events, UI styling, live_session, or asynchronous UI work.
---

# LiveView patterns

Inspect installed Phoenix/LiveView versions, generated components, auth hooks, and styling before editing. Preserve daisyUI, custom Tailwind components, or another established design system. Do not migrate dependencies merely to follow an example.

## Authentication and layouts

Use the appropriate existing `live_session` and `on_mount` hook. Create another session when distinct authentication requirements or root layouts justify the boundary. Check both HTTP and connected mounts; never start duplicate external side effects from mount.

Use `@current_scope.user` where the app has Phoenix scope-based auth. Preserve `@current_user` in older/custom auth until a scoped migration is requested. Pass the corresponding scope/user contract to contexts consistently.

Authorize page access, navigation, and mutating events. Recheck permissions/state at the domain boundary; hidden buttons and earlier mount checks do not authorize a later write.

Use the layout structure already generated for this Phoenix version. In Phoenix 1.8-style apps, render through `Layouts.app` and avoid duplicating the layout's flash group.

## Forms

Assign a `Phoenix.HTML.Form` with `to_form`, then reuse the project's form/input components. This is an illustrative HEEx fragment:

```heex
<.form for={@form} id="order-form" phx-submit="save">
  <.input field={@form[:title]} type="text" label="Title" />
  <button type="submit">Save</button>
</.form>
```

`Phoenix.Component.form/1` does not supply an `:actions` slot. Use ordinary children, or use that slot only on a project component which declares it. Validate event params server-side and preserve changeset errors on failure.

## Components and collections

Use function components for reusable markup. Use LiveComponents when independent events/lifecycle justify them; keep ownership and message flow explicit.

Use streams for large or changing collections; regular assigns are appropriate for small, bounded lists. Stream containers need a stable `id` and `phx-update="stream"`; each item must use its generated stream DOM ID. Re-fetch and reset when changing filters. Keep counts/empty states separately because streams are not ordinary enumerable collections.

## Async work and durability

Use `assign_async`/`start_async` for reads or work that may safely end with the LiveView. Capture only needed values outside the async function; do not copy the socket into the task.

Use durable jobs for work that must survive disconnects, deploys, and process loss, especially external side effects. Match enqueue failures and show meaningful UI state. A waiting user alone does not make a simple async read an Oban job.

Subscribe to scoped PubSub topics only after `connected?(socket)`. Authorization belongs in data access as well as subscription setup; avoid broadcasting sensitive payloads to broad topics. Handle updates idempotently and refresh through the scoped context where appropriate.

## JavaScript and styles

- Preserve the existing asset build and design tokens. Use daisyUI components/themes where the app adopts them, with custom Tailwind for gaps.
- For Tailwind v4, preserve CSS-based configuration; do not delete a v3 config until upgrading is in scope.
- Prefer project icon components and semantic theme colors. Check light/dark modes, keyboard use, focus, labels, and contrast.
- Use the existing global hooks map, or colocated hooks when supported by the installed LiveView version. Colocated hook names start with a dot and hook elements need unique IDs.
- Use `phx-update="ignore"` only where a hook owns the subtree; understand what server patches it prevents.
- Bundle dependencies through the existing build by default. External scripts require an intentional CSP, integrity, and deployment decision; they are not categorically incompatible with Phoenix.

## Verification

Use LiveViewTest for events, authorization, form errors, and rendered state. Use focused browser checks for JavaScript hooks, real upload integrations, focus behavior, and browser-only failures. Report visual/browser checks that were unavailable.

## References

- [LiveView security model](https://hexdocs.pm/phoenix_live_view/security-model.html)
- [LiveView async operations](https://hexdocs.pm/phoenix_live_view/Phoenix.LiveView.html#module-async-operations)
- [Phoenix 1.8 and daisyUI](https://www.phoenixframework.org/blog/phoenix-1-8-released)
