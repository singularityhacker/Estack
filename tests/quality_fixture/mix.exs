defmodule Estack.QualityFixture.MixProject do
  use Mix.Project

  def project do
    [
      app: :estack_quality_fixture,
      version: "1.0.0",
      elixir: ">= 1.14.0",
      deps: [{:credo, "~> 1.7.0", runtime: false}],
      elixirc_paths: []
    ]
  end
end
