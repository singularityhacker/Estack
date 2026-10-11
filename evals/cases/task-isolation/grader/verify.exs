Code.require_file("support.exs", __DIR__)
Code.require_file(System.fetch_env!("ESTACK_SUBMISSION"))
import ExUnit.Assertions
{:ok, supervisor} = Task.Supervisor.start_link()
# Exercise each operation in a monitored caller so a broken helper cannot kill this driver.
call = fn fun, timeout ->
  {pid, ref} =
    spawn_monitor(fn -> exit({:returned, Gateway.VendorRead.run(supervisor, fun, timeout)}) end)

  receive do
    {:DOWN, ^ref, :process, ^pid, {:returned, result}} -> result
    {:DOWN, ^ref, :process, ^pid, reason} -> {:caller_died, reason}
  after
    2_000 ->
      Process.exit(pid, :kill)
      flunk("caller did not finish")
  end
end

Workshop.Checks.run([
  {"successful_read", fn -> assert {:ok, 42} = call.(fn -> 42 end, 100) end},
  {"crash_isolated",
   fn -> assert {:error, {:task_exit, _}} = call.(fn -> raise "vendor down" end, 100) end},
  {"timeout_isolated",
   fn -> assert {:error, :timeout} = call.(fn -> Process.sleep(:infinity) end, 5) end},
  {"no_orphan_after_timeout",
   fn ->
     parent = self()

     call.(
       fn ->
         send(parent, {:worker, self()})
         Process.sleep(:infinity)
       end,
       20
     )

     assert_receive {:worker, worker}, 500
     refute Process.alive?(worker)
   end},
  {"error_value_preserved",
   fn -> assert {:ok, {:error, :upstream}} = call.(fn -> {:error, :upstream} end, 100) end},
  {"caller_mailbox_clean",
   fn ->
     send(self(), :unrelated)
     assert {:ok, :ok} = Gateway.VendorRead.run(supervisor, fn -> :ok end, 100)
     assert_receive :unrelated
     refute_receive {_reference, _value}, 20
     refute_receive {:DOWN, _, _, _, _}, 20
   end},
  {"timeout_mailbox_clean",
   fn ->
     unrelated_ref = make_ref()
     unrelated = {unrelated_ref, :unrelated}
     send(self(), unrelated)

     assert {:error, :timeout} =
              Gateway.VendorRead.run(supervisor, fn -> Process.sleep(:infinity) end, 5)

     assert_receive ^unrelated
     refute_receive {_reference, _value}, 20
     refute_receive {:DOWN, _, _, _, _}, 20
   end},
  {"crash_mailbox_clean",
   fn ->
     unrelated_ref = make_ref()
     unrelated = {:DOWN, unrelated_ref, :process, self(), :unrelated}
     send(self(), unrelated)

     assert {:error, {:task_exit, _}} =
              Gateway.VendorRead.run(supervisor, fn -> exit(:vendor_failure) end, 100)

     assert_receive ^unrelated
     refute_receive {_reference, _value}, 20
     refute_receive {:DOWN, _, _, _, _}, 20
   end}
])
