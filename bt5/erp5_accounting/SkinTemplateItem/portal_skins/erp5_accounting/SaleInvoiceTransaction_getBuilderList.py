portal_deliveries = context.getPortalObject().portal_deliveries
builder_list = []

for builder_id in ('sale_invoice_builder',
                   'sale_invoice_tax_builder',
                   'sale_invoice_transaction_builder',
                   'advanced_sale_invoice_transaction_builder', ):
  builder = getattr(portal_deliveries, builder_id, None)
  if builder is not None:
    builder_list.append(builder)

return builder_list
