from Products.ERP5Type.Core.Workflow import ValidationFailed

check_result = context.checkConsistency()
message_list = []

for err in check_result:
  if getattr(err, 'getTranslatedMessage', None) is not None:
    message_list.append(err.getTranslatedMessage())
  else:
    # backward compatibility:
    message_list.append(err[3])

if message_list:
  raise ValidationFailed(message_list)
