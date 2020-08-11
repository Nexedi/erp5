portal = context.getPortalObject()
user_reference = portal.Base_getUserCaption()

person = portal.portal_catalog.getResultValue(
                portal_type = 'Person',
                reference = user_reference)

if person:
  return '%s %s' % (person.getFirstName(), person.getLastName())
else:
  return user_reference
