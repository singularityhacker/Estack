defmodule Ledger.Invoices do
  def rename(invoices, _scope, id, attrs) do
    case Enum.find(invoices, &(&1.id == id)) do
      nil -> {:error, :not_found}
      invoice -> {:ok, Map.put(invoice, :title, attrs["title"])}
    end
  end
end
