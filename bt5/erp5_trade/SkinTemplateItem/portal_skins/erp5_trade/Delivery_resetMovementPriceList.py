# This script sets zero to the prices of all movements, so that
# prices will be recalculated.

portal = context.getPortalObject()
# We do not want to reset all kinds of movements (e.g. Accounting Movements).
portal_type_list = portal.getPortalInvoiceMovementTypeList() \
  + portal.getPortalOrderMovementTypeList() \
  + portal.getPortalDeliveryMovementTypeList()
for movement in context.getMovementList(portal_type=portal_type_list):
  movement.edit(price=None, base_unit_price=None)

if not batch_mode:
  message = context.Base_translateString('Prices reset.')
  return context.Base_redirect(form_id,
          keep_items=dict(portal_status_message=message))
