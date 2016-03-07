"""
  Find the list of objects to synchronize by calling the catalog.

  Possibly look up a single object based on its ID, GID
"""

if gid is not None and len(gid):
  gid_generator_method_id = context_document.getGidGeneratorMethodId()
  method = getattr(context_document, gid_generator_method_id)
  for person in context.getPortalObject().person_module.contentValues():
    person_gid = method(person)
    if person_gid == gid:
      return [person,]
  return []
elif id is not None and len(id):
  # work on the defined person (id is not None)
  person = getattr(context.person_module, id)
  if person.getDefaultEmailText() and \
      person.getValidationState() not in ['invalidated', 'deleted'] and \
      person.getTitle() != 'Unknown':
    return [person,]
  return []
else:
  person_list = []
  person_append = person_list.append
  # first get the related integration site
  while context_document.getParentValue().getPortalType() != "Synchronization Tool":
    context_document = context_document.getParentValue()
  site = [x for x in context_document.Base_getRelatedObjectList(portal_type="Integration Module")][0].getParentValue()

  # then browse list of stc related to the site one
  default_stc = site.getSourceTradeValue()
  for document in default_stc.Base_getRelatedObjectList(portal_type="Sale Trade Condition",
                                                        validation_state="validated"):
    dest = document.getObject().getDestinationDecisionValue()
    if dest is not None and dest.getPortalType() == "Person" and \
           dest.getValidationState() == "validated":
      person_append(dest)
  return person_list
