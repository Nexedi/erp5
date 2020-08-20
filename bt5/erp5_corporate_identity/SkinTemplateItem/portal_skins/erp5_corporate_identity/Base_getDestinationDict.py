"""
================================================================================
Create a destination dict for filling templates
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# destination:                             Can be set if called from Event
# override_destination_person_title:       Title of person to use
# override_destination_organisation_title: Title of organisation to use
# ----------------------------  Set Destination --------------------------------
# destination => Web Page = follow-up Organisation or Person, Event
if destination is None:
  destination_person = None
  destination_person_list = []
  destination_organisation = None
  destination_organisation_list = []
  destination_uid = None

  # destination person
  if override_destination_person_title:
    destination_person_list = context.Base_getTemplateProxyParameter(parameter="override_person", source_data=override_destination_person_title)
  if not destination_person_list:
    # follow up
    destination_person_list = context.Base_getTemplateProxyParameter(parameter="person", source_data=None)
  if destination_person_list:
    destination_person = destination_person_list[0]

  # destination organisation
  if override_destination_organisation_title:
    destination_organisation_list = context.Base_getTemplateProxyParameter(parameter="override_organisation", source_data=override_destination_organisation_title)
  if not destination_organisation_list:
    #follow up value
    destination_organisation_list = context.Base_getTemplateProxyParameter(parameter="organisation", source_data=None)
  if not destination_organisation_list and destination_person:
    # person 's Career Subordination or itself if no career subordination
    destination_organisation_list = context.Base_getTemplateProxyParameter(parameter="source", source_data=destination_person.get("uid")) or []
  if destination_organisation_list:
    destination_organisation = destination_organisation_list[0]

  destination = {}
  destination.update(destination_person or {})
  destination.update(destination_organisation or {})

# destination => event
else:
  destination_uid = context.restrictedTraverse(destination).getUid()
  destination = context.Base_getTemplateProxyParameter(parameter="destination", source_data=destination_uid)[0]

return destination
