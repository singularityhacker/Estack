defmodule Inbox.Webhook do
  def receive(raw_body, verify, persist) do
    with {:ok, event} <- verify.(raw_body) do
      case persist.(event) do
        :ok -> {:ok, 202}
        {:error, :duplicate} -> {:ok, 200}
        {:error, _} -> {:error, 503}
      end
    else
      {:error, :invalid_signature} -> {:error, 401}
    end
  end
end
