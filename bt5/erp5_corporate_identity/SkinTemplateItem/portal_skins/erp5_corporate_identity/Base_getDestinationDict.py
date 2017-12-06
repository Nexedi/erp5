"""
================================================================================
Create a destination dict for filling templates
================================================================================
"""
blank = ''
from Products.PythonScripts.standard import html_quote

# --------------------------  External parameters ------------------------------

# eg "Nexedi" specific parameters
customHandler = getattr(context, "WebPage_getCustomParameter", None)

# parameters common to all templates
commonHandler = getattr(context, "WebPage_getCommonParameter", None)
commonProxyHandler = getattr(context, "WebPage_getCommonProxyParameter", None)

def getCustomParameter(my_parameter, my_override_data):
  if customHandler is not None:
    source_data = my_override_data or context.getUid()
    return customHandler(parameter=my_parameter, source_data=source_data)

def getCommonParameter(my_parameter, my_override_data):
  if commonHandler is not None:
    source_data = my_override_data or context.getUid()
    return commonHandler(parameter=my_parameter, source_data=source_data)

def getCommonProxyParameter(my_parameter, my_override_data):
  if commonProxyHandler is not None:
    source_data = my_override_data or context.getUid()
    return commonProxyHandler(parameter=my_parameter, source_data=source_data)

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
    destination_person_list = getCommonProxyParameter("override_person", override_destination_person_title)
  if len(destination_person_list) == 0:
    destination_person_list = getCommonProxyParameter("person", None)
  if len(destination_person_list) > 0:
    destination_person = destination_person_list[0]

  # destination organisation
  if override_destination_organisation_title is not None or override_destination_organisation_title is blank:
    destination_organisation_list = getCommonProxyParameter("override_organisation", override_destination_organisation_title)
  if len(destination_organisation_list) == 0:
    destination_organisation_list = getCommonProxyParameter("organisation", None)
  if len(destination_organisation_list) == 0 and destination_person is not None:
    destination_organisation_list = getCommonProxyParameter("source", destination_person.get("uid")) or []
  if len(destination_organisation_list) > 0:
    destination_organisation = destination_organisation_list[0]

  destination = {}
  destination.update(destination_person or {})
  destination.update(destination_organisation or {})
  
# destination => event
else:
  destination_uid = context.restrictedTraverse(destination).getUid()
  destination = getCommonProxyParameter("destination", destination_uid)

return destination
