def getMyOrganisationUidList():
  main_organisation = context.Base_getMyMainOrganisation()
  organisation_set = set()
  organisation_set.add(main_organisation.getUid())
  for document in main_organisation.getBusinessConnectionRelatedValueList(portal_type='Organisation'):
    organisation_set.add(document.getUid())
  return list(organisation_set)

key = '__cache'+script.id

try:
  return int(context.getUid() in context.REQUEST.form[key])
except KeyError:
  context.REQUEST.form[key] = getMyOrganisationUidList()
  return int(context.getUid() in context.REQUEST.form[key])
