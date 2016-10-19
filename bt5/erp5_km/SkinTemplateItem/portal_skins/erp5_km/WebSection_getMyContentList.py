"""
  This scripts lists the documents belonging to a given Person.
  If it is called on a Person object, it lists the documents
  which belong to that person. If it is called on another type
  of object, it lists the document which belong to the current
  user.
"""
if context.getPortalType() == 'Person':
  # If context is a person, get the user
  user = context.Person_getUserId()
  if user is None:
    # no way to determine documents if we have no reference
    return []
  return context.ContributionTool_getMyContentList(user=user, **kw)
else:
  return context.ContributionTool_getMyContentList(**kw)
