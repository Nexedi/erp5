try:
  context.SaleInvoiceTransaction_sendInvoiceDetailRequest()
except AssertionError as e:
  context.Base_redirect(keep_items={"portal_status_message": str(e),
                                    "portal_status_level": "error"})
else:
  context.Base_redirect(keep_items={"portal_status_message":
                  context.Base_translateString('Cxml Invoice sent.')})
