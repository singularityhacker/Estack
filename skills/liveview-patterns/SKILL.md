---
name: liveview-patterns
description: LiveView conventions for Phoenix apps. Auth sessions, forms, components, streams, hooks, and state management. Use when building or modifying LiveView pages.
---

# LiveView Patterns

## Auth is a live_session

Logged-in pages sit in one `live_session` whose `on_mount` hook sets `@current_scope`:

```elixir
live_session :require_authenticated_user,
  on_mount: [{MyAppWeb.UserAuth, :require_authenticated}] do
  live "/dashboard", DashboardLive, :index
end
```

**Rules:**
- Add new authenticated LiveViews inside the existing `live_session` block.
- Pass `current_scope` into context calls. In templates, read `@current_scope.user`.
- Do not invent a new `live_session` name.
- Do not assign `@current_user` -- use `@current_scope.user`.

## Layouts

Templates start with `<Layouts.app flash={@flash} ...>`. The flash group is rendered only from `layouts.ex`. Do not render the flash group yourself.

## Forms

```elixir
# In mount or handle_event:
form = to_form(changeset)
{:ok, assign(socket, form: form)}
```

```heex
<.form for={@form} phx-submit="save">
  <.input field={@form[:title]} label="Title" />
  <:actions><button>Save</button></:actions>
</.form>
```

**Rules:**
- Assign the form with `to_form/2`. Give it a stable DOM id.
- Use `<.input>`. Do not pass a changeset to `<.form>`.
- Do not use `form_for` or `<.form let={f}>`.

## LiveComponents are the exception

Almost every screen should be a LiveView. Extract a function component for markup reuse. Reach for `LiveComponent` only when the widget handles its own events and would bloat the parent.

Do not use a LiveComponent for a static chunk of markup -- that splits state you then have to message back.

## Streams

Use streams for the one collection that grows during the session:

```elixir
socket
|> stream(:messages, messages, reset: true)
```

```heex
<div id="messages" phx-update="stream">
  <div :for={{dom_id, msg} <- @streams.messages} id={dom_id}>
    <%= msg.body %>
  </div>
</div>
```

**Rules:**
- Set `phx-update="stream"` and a DOM id on the parent.
- Use the stream's dom_id on each child.
- To filter, re-fetch and `stream(..., reset: true)`.
- Track counts in a separate assign.
- Leave short, static lists as ordinary assigns.

## Long work goes to Oban

`start_async` dies when the user refreshes. If the user is waiting on the result, persist through an Oban worker:

```elixir
# Good: survives disconnect
Oban.insert(DocFillJob.new(%{company_id: company.id, doc_key: key}))

# Risky: lost on refresh
start_async(socket, :fill, fn -> fill_document(company, key) end)
```

Use `start_async` only for work that is safe to abandon on disconnect.

## Hooks

- Global hooks go in `assets/js/app.js` and are added to the `hooks` map.
- Colocated hooks go in the HEEx file with a leading dot name:

```heex
<script :type={Phoenix.LiveView.ColocatedHook} name=".CopyButton">
  export default {
    mounted() { /* ... */ }
  }
</script>
<button phx-hook=".CopyButton" id="copy-btn">Copy</button>
```

If the hook owns its DOM, set `phx-update="ignore"`.

## Multi-step UI

Model a wizard as an integer or atom assign. Render the step that matches. Do not add a state-machine library.

When a tool needs confirmation, assign the pending payload and a state atom. Execute only on the confirm event.

## Styles

- Tailwind v4 with `@import "tailwindcss"` in `assets/css/app.css`.
- No `tailwind.config.js`. No daisyUI.
- Icons via `<.icon name="hero-...">`.
- No external `<script>` tags or CDN stylesheets. They break CSP.
- No `@apply`.

## One LiveView, multiple actions

If the new route is another mode of the same screen, add a `live_action` and branch in `handle_params`:

```elixir
live "/orders", OrdersLive, :index
live "/orders/new", OrdersLive, :new
live "/orders/:id", OrdersLive, :show
```

If it is a different screen with different events, add `live/feature_live/<screen>.ex` with a nested module name.
