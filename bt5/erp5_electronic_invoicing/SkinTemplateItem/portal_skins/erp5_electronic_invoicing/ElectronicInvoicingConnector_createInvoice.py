portal = context.getPortalObject()

invoice_id = context.getTypeBasedMethod("getInvoiceId")(invoice_dict)
text_content = context.getInvoice(invoice_id)

# If an invoice with the same id was already processed, ignore silently.
# This allows resetting the connector if needed to reprocess everything.
matching_invoice = portal.portal_catalog(
  portal_type="Electronic Invoice",
  reference=invoice_id,
  limit=1,
)
if len(matching_invoice) > 0:
  return

kw = context.getTypeBasedMethod("getInvoiceExtraPropertyList")(text_content)
invoice_value = portal.electronic_invoice_module.newContent(
  portal_type="Electronic Invoice",
  reference=invoice_id,
  # Store from which connector the invoice comes from
  source_value=context,
  destination_section=context.getDestinationSection(),
  text_content=text_content,
  **kw,
)
invoice_value.send()
