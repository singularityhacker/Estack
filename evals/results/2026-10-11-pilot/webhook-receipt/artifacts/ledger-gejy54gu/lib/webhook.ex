defmodule Inbox.Webhook do
  def receive(raw_body, verify, persist) do
    case verify.(raw_body) do
      {:ok, event} ->
        case persist.(event) do
          :ok -> {:ok, 202}
          {:error, :duplicate} -> {:ok, 200}
          {:error, _reason} -> {:error, 503}
        end

      {:error, :invalid_signature} -> {:error, 401}
    end
  end
end
