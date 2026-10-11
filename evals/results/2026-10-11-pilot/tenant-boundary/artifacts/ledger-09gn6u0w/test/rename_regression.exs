ExUnit.start()
Code.require_file("../lib/invoices.ex", __DIR__)

defmodule Ledger.RenameRegressionTest do
  use ExUnit.Case

  @invoice %{id: 1, tenant_id: 10, owner_id: 2, title: "Old"}
  @owner %{tenant_id: 10, role: :owner}
  @viewer %{tenant_id: 10, role: :viewer}

  test "owner preserves submitted whitespace and ignores other fields" do
    attrs = %{
      "title" => "  New title\n",
      "id" => 99,
      "tenant_id" => 99,
      "owner_id" => 99,
      "extra" => "ignored"
    }

    assert {:ok, updated} = Ledger.Invoices.rename([@invoice], @owner, 1, attrs)
    assert updated == %{@invoice | title: "  New title\n"}
  end

  test "missing and other-tenant invoices are not found regardless of role or title" do
    for scope <- [@owner, @viewer], attrs <- [%{"title" => "New"}, %{}] do
      assert {:error, :not_found} = Ledger.Invoices.rename([@invoice], scope, 99, attrs)

      assert {:error, :not_found} =
               Ledger.Invoices.rename([@invoice], %{scope | tenant_id: 20}, 1, attrs)
    end
  end

  test "lookup selects the matching tenant even when another tenant has the same id" do
    other_invoice = %{@invoice | tenant_id: 20}

    assert {:ok, updated} =
             Ledger.Invoices.rename([other_invoice, @invoice], @owner, 1, %{"title" => "New"})

    assert updated == %{@invoice | title: "New"}
  end

  test "viewers cannot rename visible invoices regardless of title validity" do
    for attrs <- [%{"title" => "New"}, %{"title" => " "}, %{}] do
      assert {:error, :forbidden} = Ledger.Invoices.rename([@invoice], @viewer, 1, attrs)
    end
  end

  test "owners must supply a nonblank string title" do
    for title <- [nil, "", " \t\r\n", "\u00A0", 42, false, [], %{}] do
      assert {:error, :invalid_title} =
               Ledger.Invoices.rename([@invoice], @owner, 1, %{"title" => title})
    end

    assert {:error, :invalid_title} = Ledger.Invoices.rename([@invoice], @owner, 1, %{})
  end
end
