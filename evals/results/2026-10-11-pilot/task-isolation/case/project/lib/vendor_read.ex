defmodule Gateway.VendorRead do
  def run(supervisor, fun, timeout) do
    task = Task.Supervisor.async_nolink(supervisor, fun)
    {:ok, Task.await(task, timeout)}
  end
end
