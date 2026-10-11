ExUnit.start()
Code.require_file("../lib/invoices.ex", __DIR__)
defmodule Ledger.SmokeTest do
  use ExUnit.Case
  test "owner renames an invoice" do
    invoices = [%{id: 1, tenant_id: 10, owner_id: 2, title: "Old"}]
    assert {:ok, %{title: "New"}} = Ledger.Invoices.rename(invoices, %{tenant_id: 10, role: :owner}, 1, %{"title" => "New"})
  end
end
