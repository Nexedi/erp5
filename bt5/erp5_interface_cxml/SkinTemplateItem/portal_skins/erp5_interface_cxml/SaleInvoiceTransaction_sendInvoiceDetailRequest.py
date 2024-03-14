#context = state_change['object']
# only send ShipNoticeRequest if the Sale Packing List is related to
# a Sale Order which is related to a valid Cxml Order Request
if not context.Base_isCxmlRelated():
  return
text_content = context.SaleInvoiceTranaction_getInvoiceDetailRequest().encode('utf-8')
connector = context.Base_getCxmlConnectorValueForSale()
connector.sendOutgoingRequest(text_content, follow_up=context.getRelativeUrl())
