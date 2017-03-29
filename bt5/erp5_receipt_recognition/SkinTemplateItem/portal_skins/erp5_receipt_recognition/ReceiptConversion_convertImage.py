image = context.getSource()
portal = context.getPortalObject()
image = portal.restrictedTraverse(image)
try:
  total = container.find_receipt_value(image.getData())
  msg = "Total found"
  context.edit(
    total = total,
  )
except Exception as e:
  msg = "Could not find value, please submit it manually"

if batch_mode:
  return

context.Base_redirect(
  'view', keep_items = dict(portal_status_message=msg, my_source="test"))
