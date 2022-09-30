"""Create the related person and the related organisation
Return related person and related organisation
Proxy:
Auditor -- to be able to get destination_decision
Author -- to be able to call newContent
Assignee -- to be able to call setDestinationDecisionValueList"""

# check the script is not called from a url
if REQUEST is not None:
  return None

destination_list = context.getDestinationDecisionValueList()
update_destination_list = False
for destination in destination_list:
  try:
    create_portal_type.remove(destination.getPortalType())
  except ValueError:
    #Portal type is not present
    pass

if "Organisation" in create_portal_type:
  #Try to find existant organisation
  organisation_title = context.getOrganisationTitle()
  module = context.getDefaultModule("Organisation")
  organisation_list = module.searchFolder(title=organisation_title)
  #be sure we have the same title and no %title%
  organisation_list = [x.getObject() for x in organisation_list if x.getObject().getTitle() == organisation_title ]
  if organisation_list:
    destination_list.append(organisation_list[0])
    create_portal_type.remove("Organisation")
    update_destination_list = True

for portal_type in create_portal_type:
  update_destination_list = True
  module = context.getDefaultModule(portal_type)
  obj = module.newContent(portal_type=portal_type)
  destination_list.append(obj)

if update_destination_list:
  context.setDestinationDecisionValueList(destination_list)
