portal_deliveries = context.getPortalObject().portal_deliveries
builder_list = []

for builder_id in ('purchase_invoice_builder',
                   'purchase_invoice_tax_builder',
                   'purchase_invoice_transaction_builder',
                   'advanced_purchase_invoice_transaction_builder', ):
  builder = getattr(portal_deliveries, builder_id, None)
  if builder is not None:
    builder_list.append(builder)

return builder_list
