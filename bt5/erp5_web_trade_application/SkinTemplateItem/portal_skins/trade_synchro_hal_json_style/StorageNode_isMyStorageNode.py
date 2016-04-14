for organisation in context.getBusinessConnectionValueList(portal_type='Organisation'):
  result = int(organisation is not None and organisation.Organisation_isMyOrganisation())
  if result:
    return result
return 0
