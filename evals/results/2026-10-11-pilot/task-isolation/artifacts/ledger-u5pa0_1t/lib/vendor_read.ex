defmodule Gateway.VendorRead do
  def run(supervisor, fun, timeout) do
    task = Task.Supervisor.async_nolink(supervisor, fun)

    case Task.yield(task, timeout) do
      {:ok, value} ->
        {:ok, value}

      {:exit, reason} ->
        {:error, {:task_exit, reason}}

      nil ->
        Task.shutdown(task, :brutal_kill)
        {:error, :timeout}
    end
  end
end
