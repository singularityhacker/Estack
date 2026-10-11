defmodule Inbox.Webhook do
  def receive(raw_body, verify, persist) do
    case verify.(raw_body) do
      {:ok, event} ->
        _ = persist.(event)
        {:ok, 202}

      {:error, :invalid_signature} ->
        {:error, 401}
    end
  end
end
