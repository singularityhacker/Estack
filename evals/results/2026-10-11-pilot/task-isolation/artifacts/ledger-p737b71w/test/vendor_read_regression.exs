ExUnit.start()
Code.require_file("../lib/vendor_read.ex", __DIR__)

defmodule Gateway.VendorReadRegressionTest do
  use ExUnit.Case

  import ExUnit.CaptureLog

  setup do
    %{supervisor: start_supervised!({Task.Supervisor, []})}
  end

  test "wraps returned error tuples as successful values", %{supervisor: supervisor} do
    send(self(), :unrelated)

    assert {:ok, {:error, :unavailable}} =
             Gateway.VendorRead.run(supervisor, fn -> {:error, :unavailable} end, 100)

    assert_receive :unrelated
    assert {:messages, []} = Process.info(self(), :messages)
  end

  test "reports task exits without exiting the caller", %{supervisor: supervisor} do
    send(self(), :unrelated)

    capture_log(fn ->
      assert {:error, {:task_exit, :vendor_failed}} =
               Gateway.VendorRead.run(supervisor, fn -> exit(:vendor_failed) end, 100)
    end)

    assert_receive :unrelated
    assert {:messages, []} = Process.info(self(), :messages)
  end

  test "reports raised exceptions as task exits", %{supervisor: supervisor} do
    capture_log(fn ->
      assert {:error, {:task_exit, {%RuntimeError{message: "vendor failed"}, stacktrace}}} =
               Gateway.VendorRead.run(supervisor, fn -> raise "vendor failed" end, 100)

      assert is_list(stacktrace)
    end)

    assert {:messages, []} = Process.info(self(), :messages)
  end

  test "kills timed-out work even when it traps exits and cleans task messages", %{
    supervisor: supervisor
  } do
    caller = self()
    send(caller, :unrelated)

    assert {:error, :timeout} =
             Gateway.VendorRead.run(
               supervisor,
               fn ->
                 Process.flag(:trap_exit, true)
                 send(caller, {:vendor_started, self()})

                 receive do
                   :finish -> :finished
                 end
               end,
               100
             )

    assert_receive :unrelated
    assert_receive {:vendor_started, vendor}
    refute Process.alive?(vendor)
    assert Task.Supervisor.children(supervisor) == []
    assert {:messages, []} = Process.info(self(), :messages)
  end
end
