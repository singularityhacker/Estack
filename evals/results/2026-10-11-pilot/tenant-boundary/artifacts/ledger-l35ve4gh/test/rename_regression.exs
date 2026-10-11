ExUnit.start()
Code.require_file("../lib/invoices.ex", __DIR__)

defmodule Ledger.RenameRegressionTest do
  use ExUnit.Case

  @invoice %{id: 1, tenant_id: 10, owner_id: 2, title: "Old"}
  @owner %{tenant_id: 10, role: :owner}
  @viewer %{tenant_id: 10, role: :viewer}

  test "owners can rename invoices in their tenant while preserving title whitespace" do
    assert {:ok, Map.put(@invoice, :title, "  New\n")} ==
             Ledger.Invoices.rename([@invoice], @owner, 1, %{"title" => "  New\n"})
  end

  test "missing and other-tenant invoices are not found for either role" do
    for role <- [:owner, :viewer] do
      scope = %{tenant_id: 20, role: role}

      assert {:error, :not_found} =
               Ledger.Invoices.rename([@invoice], scope, 1, %{"title" => ""})

      assert {:error, :not_found} =
               Ledger.Invoices.rename([@invoice], %{scope | tenant_id: 10}, 99, %{})
    end
  end

  test "lookup finds only a matching invoice in the caller's tenant" do
    other_invoice = %{@invoice | tenant_id: 20}

    assert {:ok, Map.put(@invoice, :title, "New")} ==
             Ledger.Invoices.rename([other_invoice, @invoice], @owner, 1, %{"title" => "New"})
  end

  test "viewers cannot rename visible invoices regardless of title validity" do
    for attrs <- [%{"title" => "New"}, %{"title" => ""}, %{}] do
      assert {:error, :forbidden} = Ledger.Invoices.rename([@invoice], @viewer, 1, attrs)
    end
  end

  test "blank and non-string titles are invalid" do
    for title <- ["", " \t\r\n", "\u00A0", nil, 42, false, [], %{}] do
      assert {:error, :invalid_title} =
               Ledger.Invoices.rename([@invoice], @owner, 1, %{"title" => title})
    end

    assert {:error, :invalid_title} = Ledger.Invoices.rename([@invoice], @owner, 1, %{})
  end

  test "other params cannot change stored fields or grant edit permission" do
    attrs = %{
      "title" => "New",
      "id" => 99,
      "tenant_id" => 20,
      "owner_id" => 77,
      "role" => :owner,
      "extra" => true
    }

    assert {:ok, Map.put(@invoice, :title, "New")} ==
             Ledger.Invoices.rename([@invoice], @owner, 1, attrs)

    assert {:error, :forbidden} = Ledger.Invoices.rename([@invoice], @viewer, 1, attrs)
  end
end
