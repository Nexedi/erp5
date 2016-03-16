"""
  Determine if listbox action widget can be show or not in context.
"""

request = context.REQUEST
portal = context.getPortalObject()
list_mode = request.get('list_mode', False)
dialog_mode = request.get('dialog_mode', False)
list_style = request.get('list_style', None)
context_portal_type = context.getPortalType()

if portal.portal_membership.isAnonymousUser() or \
  dialog_mode == True or \
  (list_mode and list_style=='search'):
  return False

# show listbox action widget for module containers only
if not context_portal_type.endswith('Module'):# and context_portal_type!='Web Site':
  return False

return True
