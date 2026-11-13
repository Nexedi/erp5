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

# Create aggregated PDF
group = context.getDestinationSectionValue().getGroupValue()
document_value = portal.document_module.newContent(
  portal_type="PDF",
  title="Invoice %s" % invoice_id,
  reference="%s-INVOICE-%s" % (group.getCodification(), invoice_id),
  content_type="application/pdf",
  data=context.getInvoice(invoice_id, invoice_format="factur-x"),
  group=group.getRelativeUrl(),
  classification="collaborative/accounting",
)
document_value.share()

kw = context.getTypeBasedMethod("getInvoiceExtraPropertyList")(text_content)
invoice_value = portal.electronic_invoice_module.newContent(
  portal_type="Electronic Invoice",
  reference=invoice_id,
  # Store from which connector the invoice comes from
  source_value=context,
  destination_section=context.getDestinationSection(),
  text_content=text_content,
  aggregate=document_value.getRelativeUrl(),
  **kw,
)
invoice_value.send()
