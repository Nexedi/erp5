text_content = context.SalePackingList_getShipNoticeRequest().encode('utf-8')
connector = context.Base_getCxmlConnectorValueForSale()
connector.sendOutgoingRequest(text_content, follow_up=context.getRelativeUrl())
