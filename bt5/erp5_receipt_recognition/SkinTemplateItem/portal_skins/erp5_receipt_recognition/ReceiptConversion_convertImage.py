image = context.getFollowUpValue()
if image is not None:
  try:
    total = container.ReceiptRecognition_getReceiptValue(image.getData())
    msg = "Total found"
    context.edit(
      total = total,
    )
  except ValueError as e:
    msg = "Could not find value, please submit it manually"
else:
  msg = "Cannot find the image"

if batch_mode:
  return

context.Base_redirect(
  'view', keep_items = dict(portal_status_message=msg, my_source="test"))
