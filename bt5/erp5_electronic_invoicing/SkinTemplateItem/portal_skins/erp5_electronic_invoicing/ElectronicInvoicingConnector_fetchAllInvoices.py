for invoice_dict in context.getIncomingInvoiceList():
  context.activate().ElectronicInvoicingConnector_createInvoice(invoice_dict)
