ExUnit.start()
Code.require_file("../lib/webhook.ex", __DIR__)
defmodule Inbox.SmokeTest do
  use ExUnit.Case
  test "accepts a stored event" do
    assert {:ok, 202} = Inbox.Webhook.receive("payload", fn _ -> {:ok, %{id: "e1"}} end, fn _ -> :ok end)
  end
end
