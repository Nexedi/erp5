context.SaleOrder_checkCxmlOrderRequestConsistency(fixit=True)

if not batch_mode:
  portal = context.getPortalObject()
  translate = portal.Base_translateString
  keep_items = {'portal_status_message': translate('Changes from Order Request applied.')}
  return context.Base_redirect(form_id, keep_items=keep_items)
