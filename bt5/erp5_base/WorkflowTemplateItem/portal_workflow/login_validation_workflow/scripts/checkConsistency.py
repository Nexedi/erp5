# XXX: Duplicates Base_checkConsistency so proxy role is really effective.
from Products.ERP5Type.Core.Workflow import ValidationFailed
message_list = [x.getTranslatedMessage() for x in state_change['object'].checkConsistency()]
if message_list:
  raise ValidationFailed(message_list)
