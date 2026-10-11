Code.require_file("support.exs", __DIR__)
Code.require_file(System.fetch_env!("ESTACK_SUBMISSION"))
import ExUnit.Assertions
verify = fn _ -> {:ok, %{id: "e1"}} end

Workshop.Checks.run([
  {"receipt_before_ack",
   fn ->
     parent = self()

     assert {:ok, 202} =
              Inbox.Webhook.receive("body", verify, fn event ->
                assert event == %{id: "e1"}
                send(parent, :persisted)
                :ok
              end)

     assert_received :persisted
   end},
  {"persist_failure_retried",
   fn ->
     assert {:error, 503} =
              Inbox.Webhook.receive("body", verify, fn _ -> {:error, :database_down} end)
   end},
  {"duplicate_acknowledged",
   fn ->
     assert {:ok, 200} = Inbox.Webhook.receive("body", verify, fn _ -> {:error, :duplicate} end)
   end},
  {"invalid_signature_rejected",
   fn ->
     assert {:error, 401} =
              Inbox.Webhook.receive("body", fn _ -> {:error, :invalid_signature} end, fn _ ->
                flunk("must not persist")
              end)
   end},
  {"raw_body_preserved",
   fn ->
     raw = " {\"id\":1}\n"

     assert {:ok, 202} =
              Inbox.Webhook.receive(
                raw,
                fn bytes ->
                  assert bytes == raw
                  {:ok, :event}
                end,
                fn :event -> :ok end
              )
   end},
  {"unexpected_persistence_failure",
   fn ->
     assert_raise RuntimeError, "adapter crash", fn ->
       Inbox.Webhook.receive("body", verify, fn _ -> raise "adapter crash" end)
     end
   end}
])
