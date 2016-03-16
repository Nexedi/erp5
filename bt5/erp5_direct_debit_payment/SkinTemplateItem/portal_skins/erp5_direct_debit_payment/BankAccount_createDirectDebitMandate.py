from Products.ERP5Type.Message import translateString

direct_debit_mandate = context.getPortalObject().direct_debit_mandate_module.newContent(
  portal_type='Direct Debit Mandate',
  source_value=context.getParentValue(),
  source_payment_value=context,
  destination=destination,
  start_date=start_date)

return direct_debit_mandate.Base_redirect('view',
    keep_items=dict(portal_status_message=translateString('Direct debit mandate created.')))
