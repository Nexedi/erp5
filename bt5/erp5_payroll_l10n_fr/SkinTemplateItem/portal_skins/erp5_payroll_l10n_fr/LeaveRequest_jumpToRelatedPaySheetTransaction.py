transaction = context.LeaveRequest_getRelatedPaySheetTransaction()
translateString = context.Base_translateString

if transaction is not None:
  return transaction.Base_redirect("view",
    keep_items={
      'portal_status_message': translateString('Related Pay Sheet Transaction.')})

return context.Base_redirect("view",
    keep_items={
      'portal_status_message': translateString('No Related Pay Sheet Transaction.')})
