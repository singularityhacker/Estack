ExUnit.start()
{:ok, _} = Application.ensure_all_started(:credo)
Code.require_file("../../../skills/estack-quality/assets/discarded_result.ex", __DIR__)
