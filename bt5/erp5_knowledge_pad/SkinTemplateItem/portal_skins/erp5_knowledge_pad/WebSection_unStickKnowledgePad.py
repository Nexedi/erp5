knowledge_pad = context.restrictedTraverse(knowledge_pad_url)
knowledge_pad.delete()

return context.Base_redirect(cancel_url, keep_items={
  "portal_status_message": context.Base_translateString('Unsticked.')})
