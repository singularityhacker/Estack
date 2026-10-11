defmodule Gateway.VendorRead do
  def run(supervisor, fun, timeout) do
    task = Task.Supervisor.async_nolink(supervisor, fun)

    case Task.yield(task, timeout) || Task.shutdown(task, :brutal_kill) do
      {:ok, result} -> {:ok, result}
      {:exit, reason} -> {:error, {:task_exit, reason}}
      nil -> {:error, :timeout}
    end
  end
end
