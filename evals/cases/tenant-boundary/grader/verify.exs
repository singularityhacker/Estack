Code.require_file("support.exs", __DIR__)
Code.require_file(System.fetch_env!("ESTACK_SUBMISSION"))
import ExUnit.Assertions

invoices = [
  %{id: 1, tenant_id: 10, owner_id: 2, title: "Old"},
  %{id: 2, tenant_id: 20, owner_id: 3, title: "Other"}
]

owner = %{tenant_id: 10, role: :owner}

Workshop.Checks.run([
  {"owner_update",
   fn ->
     assert {:ok, %{title: " New "}} =
              Ledger.Invoices.rename(invoices, owner, 1, %{"title" => " New "})
   end},
  {"cross_tenant_denied",
   fn ->
     assert {:error, :not_found} =
              Ledger.Invoices.rename(invoices, owner, 2, %{"title" => "Stolen"})
   end},
  {"viewer_denied",
   fn ->
     assert {:error, :forbidden} =
              Ledger.Invoices.rename(invoices, %{owner | role: :viewer}, 1, %{"title" => "Edit"})
   end},
  {"ownership_preserved",
   fn ->
     assert {:ok, invoice} =
              Ledger.Invoices.rename(invoices, owner, 1, %{
                "title" => "New",
                "tenant_id" => 20,
                "owner_id" => 99,
                "id" => 9,
                "arbitrary" => "value"
              })

     assert invoice == %{id: 1, tenant_id: 10, owner_id: 2, title: "New"}
   end},
  {"unknown_invoice",
   fn ->
     assert {:error, :not_found} =
              Ledger.Invoices.rename(invoices, owner, 999, %{"title" => "New"})
   end},
  {"invalid_title",
   fn ->
     for title <- [nil, 7, "", "  "] do
       assert {:error, :invalid_title} =
                Ledger.Invoices.rename(invoices, owner, 1, %{"title" => title})
     end
   end}
])
