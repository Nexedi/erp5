"""Refuse changing the id of an object with pending activities.

"""
document = context.aq_parent.aq_parent.aq_parent

if editor != document.getId():
  return not document.hasActivity()

return True
