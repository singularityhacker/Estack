ExUnit.start(autorun: false)

defmodule Workshop.Checks do
  def run(checks) do
    results =
      Enum.map(checks, fn {id, check} ->
        try do
          check.()
          %{id: id, passed: true, detail: "passed"}
        rescue
          error -> %{id: id, passed: false, detail: Exception.message(error)}
        catch
          kind, reason -> %{id: id, passed: false, detail: inspect({kind, reason})}
        end
      end)

    IO.puts("ESTACK_RESULT " <> JSON.encode!(%{checks: results}))
    if Enum.any?(results, &(not &1.passed)), do: System.halt(1)
  end
end
