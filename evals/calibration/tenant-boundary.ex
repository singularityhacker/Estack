defmodule Ledger.Invoices do
  def rename(invoices, %{tenant_id: tenant, role: role}, id, attrs) do
    invoice = Enum.find(invoices, &(&1.tenant_id == tenant and &1.id == id))
    title = attrs["title"]

    cond do
      is_nil(invoice) -> {:error, :not_found}
      role != :owner -> {:error, :forbidden}
      not is_binary(title) -> {:error, :invalid_title}
      String.trim(title) == "" -> {:error, :invalid_title}
      true -> {:ok, %{invoice | title: title}}
    end
  end
end
