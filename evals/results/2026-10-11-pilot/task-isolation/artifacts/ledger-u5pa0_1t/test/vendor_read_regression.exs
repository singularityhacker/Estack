ExUnit.start()
Code.require_file("../lib/vendor_read.ex", __DIR__)

defmodule Gateway.VendorReadRegressionTest do
  use ExUnit.Case

  setup do
    %{supervisor: start_supervised!({Task.Supervisor, []})}
  end

  test "wraps returned error tuples as successful values", %{supervisor: supervisor} do
    assert {:ok, {:error, :unavailable}} =
             Gateway.VendorRead.run(supervisor, fn -> {:error, :unavailable} end, 100)

    assert {:messages, []} = Process.info(self(), :messages)
  end

  @tag capture_log: true
  test "returns task exits without exiting the caller", %{supervisor: supervisor} do
    assert {:error, {:task_exit, :vendor_failed}} =
             Gateway.VendorRead.run(supervisor, fn -> exit(:vendor_failed) end, 100)

    assert {:messages, []} = Process.info(self(), :messages)
  end

  @tag capture_log: true
  test "preserves exception details", %{supervisor: supervisor} do
    assert {:error, {:task_exit, {%RuntimeError{message: "vendor failure"}, stacktrace}}} =
             Gateway.VendorRead.run(supervisor, fn -> raise "vendor failure" end, 100)

    assert is_list(stacktrace)
    assert stacktrace != []
    assert {:messages, []} = Process.info(self(), :messages)
  end

  test "stops timed-out children and preserves unrelated messages", %{supervisor: supervisor} do
    caller = self()
    unrelated_ref = make_ref()
    unrelated_result = {unrelated_ref, :unrelated_result}
    unrelated_down = {:DOWN, unrelated_ref, :process, self(), :unrelated_exit}
    send(self(), unrelated_result)
    send(self(), unrelated_down)

    assert {:error, :timeout} =
             Gateway.VendorRead.run(
               supervisor,
               fn ->
                 Process.flag(:trap_exit, true)
                 send(caller, {:worker_started, self()})

                 receive do
                   :finish -> :finished
                 end
               end,
               50
             )

    assert_received {:worker_started, worker}
    refute Process.alive?(worker)
    assert Task.Supervisor.children(supervisor) == []
    assert {:messages, [^unrelated_result, ^unrelated_down]} = Process.info(self(), :messages)
  end
end
