"""
  Find the list of objects to synchronize by calling the catalog.

  Possibly look up a single object based on its ID, GID
"""
if gid is not None and len(gid):
  gid_generator_method_id = context_document.getGidGeneratorMethodId()
  method = getattr(context_document, gid_generator_method_id)
  for org in context.getPortalObject().organisation_module.contentValues():
    org_gid = method(org)
    if org_gid == gid:
      return [org,]
  return []
elif id is not None and len(id):
  # work on the defined organisation (id is not None)
  organisation = getattr(context.organisation_module, id)
  if organisation.getValidationState() not in ['invalidated', 'deleted'] and \
      organisation.getTitle() != 'Unknown':
    return [organisation,]
  return []
else:
  organisation_list = []
  organisation_append = organisation_list.append
  # first get the related integration site
  while context_document.getParentValue().getPortalType() != "Synchronization Tool":
    context_document = context_document.getParentValue()
  site = [x for x in context_document.Base_getRelatedObjectList(portal_type="Integration Module")][0].getParentValue()

  # then browse list of stc related to the site one
  default_stc = site.getSourceTradeValue()
  for document in default_stc.Base_getRelatedObjectList(portal_type="Sale Trade Condition",
                                                        validation_state="validated"):
    dest = document.getObject().getDestinationDecisionValue()
    if dest is not None and dest.getPortalType() == "Organisation" and \
           dest.getValidationState() == "validated":
      organisation_append(dest)
  return organisation_list
