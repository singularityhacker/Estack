ExUnit.start()
Code.require_file("../lib/webhook.ex", __DIR__)

defmodule Inbox.WebhookRegressionTest do
  use ExUnit.Case

  test "verifies untouched bytes and persists the verified event before accepting" do
    raw_body = <<0, 255, 13, 10>> <> " {\"id\": \"e1\"} "
    event = %{id: "e1"}

    verify = fn body ->
      assert body === raw_body
      send(self(), :verified)
      {:ok, event}
    end

    persist = fn stored_event ->
      assert_received :verified
      assert stored_event === event
      send(self(), :persisted)
      :ok
    end

    assert {:ok, 202} = Inbox.Webhook.receive(raw_body, verify, persist)
    assert_received :persisted
  end

  test "acknowledges a previously accepted duplicate" do
    assert {:ok, 200} =
             Inbox.Webhook.receive("payload", fn _ -> {:ok, :event} end, fn :event ->
               {:error, :duplicate}
             end)
  end

  test "allows retry when persistence fails" do
    for reason <- [:unavailable, :timeout, {:database, :disconnected}] do
      assert {:error, 503} =
               Inbox.Webhook.receive("payload", fn _ -> {:ok, :event} end, fn :event ->
                 {:error, reason}
               end)
    end
  end

  test "rejects an invalid signature without persisting" do
    assert {:error, 401} =
             Inbox.Webhook.receive(
               "payload",
               fn _ -> {:error, :invalid_signature} end,
               fn _ -> flunk("persistence must not run after signature failure") end
             )
  end

  test "propagates unexpected verifier exceptions without persisting" do
    assert_raise RuntimeError, "verification failed", fn ->
      Inbox.Webhook.receive(
        "payload",
        fn _ -> raise "verification failed" end,
        fn _ -> flunk("persistence must not run after verification raises") end
      )
    end
  end

  test "propagates unexpected persistence exceptions" do
    assert_raise RuntimeError, "storage failed", fn ->
      Inbox.Webhook.receive("payload", fn _ -> {:ok, :event} end, fn _ ->
        raise "storage failed"
      end)
    end
  end
end
