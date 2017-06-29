image = context.getFollowUpValue()
if image is not None:
  try:
    total = container.ReceiptRecognition_getReceiptValue(image.getData())
    message = "Total found"
    context.edit(
      total = total,
    )
  except ValueError as e:
    message = "Could not find value, please submit it manually"
else:
  message = "Cannot find the image"

if batch_mode:
  return

context.Base_redirect(
  'view', keep_items = dict(portal_status_message=message, my_source="test"))
