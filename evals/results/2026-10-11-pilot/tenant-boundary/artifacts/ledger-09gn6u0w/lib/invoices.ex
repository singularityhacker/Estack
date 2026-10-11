defmodule Ledger.Invoices do
  def rename(invoices, scope, id, attrs) do
    case Enum.find(invoices, &(&1.id == id and &1.tenant_id == scope.tenant_id)) do
      nil ->
        {:error, :not_found}

      invoice ->
        if scope.role == :owner do
          title = attrs["title"]

          if is_binary(title) and String.trim(title) != "" do
            {:ok, Map.put(invoice, :title, title)}
          else
            {:error, :invalid_title}
          end
        else
          {:error, :forbidden}
        end
    end
  end
end
