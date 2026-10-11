ExUnit.start()
Code.require_file("../lib/vendor_read.ex", __DIR__)
defmodule Gateway.SmokeTest do
  use ExUnit.Case
  test "returns the vendor value" do
    supervisor = start_supervised!({Task.Supervisor, []})
    assert {:ok, 42} = Gateway.VendorRead.run(supervisor, fn -> 42 end, 100)
  end
end
