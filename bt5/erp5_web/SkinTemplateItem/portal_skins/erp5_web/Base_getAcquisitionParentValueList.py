"""
Returns the list of acquisition parents
Does not take into account security
"""

result = []
document = context

while document is not None:
  result.append(document)
  if document.getPortalType() == upper_portal_type:
    document = None   # Don't go higher
  else:
    document = document.aq_parent

return result
