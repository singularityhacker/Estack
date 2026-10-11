ExUnit.start()
Code.require_file("../lib/webhook.ex", __DIR__)

defmodule Inbox.WebhookRegressionTest do
  use ExUnit.Case

  test "verifies untouched bytes and persists the verified event before returning" do
    raw_body = <<0, 255>> <> " {\"id\": \"event-1\"}\r\n"
    event = %{id: "event-1"}
    caller = self()

    verify = fn body ->
      assert body === raw_body
      send(caller, :verified)
      {:ok, event}
    end

    persist = fn stored_event ->
      assert stored_event === event
      assert_received :verified
      send(caller, :persisted)
      :ok
    end

    assert {:ok, 202} = Inbox.Webhook.receive(raw_body, verify, persist)
    assert_received :persisted
  end

  test "acknowledges a previously accepted duplicate" do
    assert {:ok, 200} =
             Inbox.Webhook.receive("body", fn _ -> {:ok, :event} end, fn :event ->
               {:error, :duplicate}
             end)
  end

  test "returns a retryable response for persistence failures" do
    for reason <- [:unavailable, :timeout, {:database, :disconnected}] do
      assert {:error, 503} =
               Inbox.Webhook.receive("body", fn _ -> {:ok, :event} end, fn :event ->
                 {:error, reason}
               end)
    end
  end

  test "rejects an invalid signature without persistence" do
    assert {:error, 401} =
             Inbox.Webhook.receive(
               "body",
               fn _ -> {:error, :invalid_signature} end,
               fn _ -> flunk("persistence must not run for invalid signatures") end
             )
  end

  test "verification exceptions propagate without persistence" do
    assert_raise RuntimeError, "verification failed", fn ->
      Inbox.Webhook.receive(
        "body",
        fn _ -> raise "verification failed" end,
        fn _ -> flunk("persistence must not run after verification raises") end
      )
    end
  end

  test "persistence exceptions propagate" do
    assert_raise RuntimeError, "persistence failed", fn ->
      Inbox.Webhook.receive("body", fn _ -> {:ok, :event} end, fn _ ->
        raise "persistence failed"
      end)
    end
  end
end
