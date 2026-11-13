for invoice_dict in context.getIncomingInvoiceList():
  context.ElectronicInvoicingConnector_createInvoice(invoice_dict)
