pad = context.restrictedTraverse(knowledge_pad_relative_url)
try:
  # If the current active pad is deleted, activate last one.
  for other_pad in context.ERP5Site_getKnowledgePadListForUser(mode=mode):
    if other_pad != pad:
      if other_pad.getValidationState() != 'invisible':
        break
      invisible = other_pad
  else:
    invisible.visible()
  pad.delete()
  msg = 'Pad removed.'
except UnboundLocalError:
  msg = 'Can not remove the only one pad.'

return context.Base_redirect(form_id="view", keep_items={
  "portal_status_message": context.Base_translateString(msg)})
