if Code.ensure_loaded?(Credo.Check) do
  defmodule Estack.Check.DiscardedResult do
    @moduledoc "Flags explicit discards of selected fallible write results."
    use Credo.Check,
      category: :warning,
      base_priority: :high,
      param_defaults: [repo_modules: ["Repo"]],
      explanations: [
        check: "Handle a fallible write result instead of assigning it to underscore.",
        params: [repo_modules: "Repo module aliases visible at the call site."]
      ]

    @repo_writes [:insert, :update, :delete, :insert_or_update, :transaction, :transact]

    @impl true
    def run(source_file, params) do
      meta = IssueMeta.for(source_file, params)
      repos = Params.get(params, :repo_modules, __MODULE__)

      Credo.Code.prewalk(source_file, &traverse(&1, &2, meta, repos), [])
    end

    defp traverse({:=, location, [{:_, _, _}, expression]} = ast, issues, meta, repos) do
      case fallible_call(expression, repos) do
        nil ->
          {ast, issues}

        trigger ->
          issue =
            format_issue(meta,
              message: "Handle the result of #{trigger} instead of discarding it.",
              trigger: trigger,
              line_no: location[:line]
            )

          {ast, [issue | issues]}
      end
    end

    defp traverse(ast, issues, _meta, _repos), do: {ast, issues}

    defp fallible_call({:|>, _, [_input, call]}, repos), do: fallible_call(call, repos)

    defp fallible_call({{:., _, [{:__aliases__, _, parts}, function]}, _, args}, repos)
         when is_list(args) do
      module = Enum.map_join(parts, ".", &Atom.to_string/1)
      repo? = module in repos or List.last(parts) == :Repo

      if (repo? and function in @repo_writes) or
           (module == "Oban" and function == :insert) or
           (module == "Phoenix.PubSub" and function == :broadcast) do
        "#{module}.#{function}"
      end
    end

    defp fallible_call(_ast, _repos), do: nil
  end
end
