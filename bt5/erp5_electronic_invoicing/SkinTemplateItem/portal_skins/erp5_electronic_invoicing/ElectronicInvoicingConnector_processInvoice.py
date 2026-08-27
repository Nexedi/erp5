validation_state = context.getValidationState()

if validation_state == "draft":
  # Create new Invoice
  connector_value = context.getSourceValue()
  invoice_dict = connector_value.getTypeBasedMethod("createInvoice")(
    electronic_invoice=context.getRelativeUrl(),
    source_section=context.getSourceSection(),
    destination_section=context.getDestinationSection(),
    reference=context.getTitle(),
    aggregate=context.getRelativeUrl(),
  )
elif validation_state == "confirmed":
  # Sync with Invoice object
  pass
