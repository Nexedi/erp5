from Products.ERP5Type.Core.Workflow import ValidationFailed

check_result = context.checkConsistency()
message_list = []

for err in check_result:
  message = None
  if getattr(err, 'getTranslatedMessage', None) is not None:
    message = err.getTranslatedMessage()
  else:
    # backward compatibility:
    message = err[3]

  if message:
    if err.object_relative_url != context.getRelativeUrl():
      object_value = context.getPortalObject().restrictedTraverse(err.object_relative_url)
      message = context.Base_translateString("At ${portal_type} ${title}: ${original_message}", mapping={
        "portal_type": context.Base_translateString(object_value.getPortalType()),
        "title": object_value.getTitle(),
        "original_message": message,
      })
    message_list.append(message)

if message_list:
  raise ValidationFailed(message_list)
