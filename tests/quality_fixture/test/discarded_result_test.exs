defmodule Estack.DiscardedResultTest do
  use ExUnit.Case, async: true

  test "flags direct and piped fallible writes" do
    for operation <- [
          "Repo.insert(changeset)",
          "MyApp.Repo.update(changeset)",
          "Repo.delete(record)",
          "Repo.transaction(multi)",
          "Repo.transact(fun)",
          "Oban.insert(job)",
          "Phoenix.PubSub.broadcast(Server, topic, payload)",
          "changeset |> Repo.insert()"
        ] do
      assert [_] = issues("_ = #{operation}")
    end
  end

  test "accepts handled results and non-fallible constructors" do
    for expression <- [
          "{:ok, result} = Repo.insert(changeset)",
          "result = Repo.insert(changeset)",
          "_ = Repo.insert!(changeset)",
          "_ = Ecto.Multi.new()",
          "_ = Repo.all(query)",
          "_ = Other.insert(changeset)",
          "case Repo.insert(changeset) do result -> result end",
          "_ = 42"
        ] do
      assert [] = issues(expression)
    end
  end

  test "supports explicitly configured repository aliases" do
    source = source("_ = DB.insert(changeset)")
    assert [] = run_check(source, Estack.Check.DiscardedResult)

    assert [_] =
             run_check(source, Estack.Check.DiscardedResult, repo_modules: ["DB"])
  end

  test "does not claim to catch an unbound expression or arbitrary alias" do
    assert [] = issues("Repo.insert(changeset)")
    assert [] = issues("_ = Jobs.insert(job)")
  end

  defp issues(expression), do: run_check(source(expression), Estack.Check.DiscardedResult)

  defp run_check(source, check, params \\ []) do
    source_file = Credo.SourceFile.parse(source, "example.ex")
    assert source_file.status == :valid
    check.run(source_file, params)
  end

  defp source(expression) do
    """
    defmodule Example do
      def run do
        #{expression}
      end
    end
    """
  end
end
