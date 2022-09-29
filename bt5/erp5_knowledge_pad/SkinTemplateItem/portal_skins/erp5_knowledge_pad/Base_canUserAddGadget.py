"""
  Can user add a gadget on context.
  This script is useful to determine if respective "Add gadget" link should be show.
"""
request = context.REQUEST
portal = context.getPortalObject()
list_mode = request.get('list_mode', False)
dialog_mode = request.get('dialog_mode', False)
isAnonymousKnowledgePadUsed = request.get('is_anonymous_knowledge_pad_used', False)

if (portal.portal_membership.isAnonymousUser() and \
  isAnonymousKnowledgePadUsed) or \
  list_mode == True or \
  dialog_mode == True:
  return False
return True
