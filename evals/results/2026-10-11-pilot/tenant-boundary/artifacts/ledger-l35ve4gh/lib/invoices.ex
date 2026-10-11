defmodule Ledger.Invoices do
  def rename(invoices, %{tenant_id: tenant_id, role: role}, id, attrs) do
    case Enum.find(invoices, &(&1.id == id and &1.tenant_id == tenant_id)) do
      nil ->
        {:error, :not_found}

      _invoice when role != :owner ->
        {:error, :forbidden}

      invoice ->
        title = attrs["title"]

        if is_binary(title) and String.trim(title) != "" do
          {:ok, Map.put(invoice, :title, title)}
        else
          {:error, :invalid_title}
        end
    end
  end
end
