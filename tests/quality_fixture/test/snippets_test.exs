defmodule Estack.SnippetsTest do
  use ExUnit.Case
  import ExUnit.CaptureLog
  @root Path.expand("../../..", __DIR__)

  setup_all do
    for name <- ["estack-elixir", "estack-otp"],
        [_, snippet] <-
          Regex.scan(
            ~r/```elixir\n(.*?)\n```/s,
            File.read!(Path.join([@root, "skills", name, "SKILL.md"]))
          ),
        String.starts_with?(snippet, "defmodule Estack.Examples.") do
      Code.compile_string(snippet)
    end

    :ok
  end

  test "all Elixir code fences and example source assets parse" do
    for path <- Path.wildcard(Path.join(@root, "skills/*/SKILL.md")),
        [_, snippet] <- Regex.scan(~r/```elixir\n(.*?)\n```/s, File.read!(path)) do
      assert {:ok, _} = Code.string_to_quoted(snippet, file: path)
    end

    for glob <- [
          "skills/*/assets/*.ex",
          "skills/*/assets/*.ex.example",
          "skills/*/assets/*.exs.example"
        ],
        path <- Path.wildcard(Path.join(@root, glob)) do
      assert {:ok, _} = Code.string_to_quoted(File.read!(path), file: path)
    end
  end

  @tag :tmp_dir
  test "file example returns content and open errors", %{tmp_dir: dir} do
    path = Path.join(dir, "sample.txt")
    File.write!(path, "first\nsecond\n")
    assert {:ok, "first\n"} = apply(Estack.Examples.FileReader, :first_line, [path])

    assert {:error, :enoent} =
             apply(Estack.Examples.FileReader, :first_line, [path <> ".missing"])
  end

  test "isolated task example handles success, crash, and timeout" do
    supervisor = start_supervised!({Task.Supervisor, []})

    run = fn fun, timeout ->
      apply(Estack.Examples.IsolatedTask, :run, [supervisor, fun, timeout])
    end

    assert {:ok, 42} = run.(fn -> 42 end, 1_000)

    capture_log(fn ->
      assert {:error, {:task_exit, _}} = run.(fn -> raise "expected failure" end, 1_000)
    end)

    assert {:error, :timeout} = run.(fn -> Process.sleep(:infinity) end, 1)
    assert Task.Supervisor.children(supervisor) == []
  end
end
