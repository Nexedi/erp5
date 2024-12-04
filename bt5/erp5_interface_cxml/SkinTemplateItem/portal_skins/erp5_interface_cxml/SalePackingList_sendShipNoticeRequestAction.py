try:
  context.SalePackingList_sendShipNoticeRequest()
except AssertionError as e:
  context.Base_redirect(keep_items={"portal_status_message": str(e),
                                    "portal_status_level": "error"})
else:
  context.Base_redirect(keep_items={"portal_status_message":
                context.Base_translateString('Cxml Ship Notice sent.')})
