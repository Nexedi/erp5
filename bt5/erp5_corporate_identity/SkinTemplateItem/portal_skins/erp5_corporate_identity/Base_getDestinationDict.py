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

blank = ''

# ----------------------------  Set Destination --------------------------------
# destination => Web Page = follow-up Organisation or Person, Event
if destination is None:
  destination_person = None
  destination_person_list = []
  destination_organisation = None
  destination_organisation_list = []
  destination_uid = None

  # destination person
  if override_destination_person_title is not None or override_destination_person_title is blank:
    destination_person_list = context.Base_getCustomTemplateProxyParameter("override_person", override_destination_person_title)
  if len(destination_person_list) == 0:
    destination_person_list = context.Base_getCustomTemplateProxyParameter("person", None)
  if len(destination_person_list) > 0:
    destination_person = destination_person_list[0]

  # destination organisation
  if override_destination_organisation_title is not None or override_destination_organisation_title is blank:
    destination_organisation_list = context.Base_getCustomTemplateProxyParameter("override_organisation", override_destination_organisation_title)
  if len(destination_organisation_list) == 0:
    destination_organisation_list = context.Base_getCustomTemplateProxyParameter("organisation", None)
  if len(destination_organisation_list) == 0 and destination_person is not None:
    destination_organisation_list = context.Base_getCustomTemplateProxyParameter("source", destination_person.get("uid")) or []
  if len(destination_organisation_list) > 0:
    destination_organisation = destination_organisation_list[0]

  destination = {}
  destination.update(destination_person or {})
  destination.update(destination_organisation or {})

# destination => event
else:
  destination_uid = context.restrictedTraverse(destination).getUid()
  destination = context.Base_getCustomTemplateProxyParameter("destination", destination_uid)[0]

return destination
