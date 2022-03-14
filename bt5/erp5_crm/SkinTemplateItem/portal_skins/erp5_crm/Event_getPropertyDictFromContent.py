"""
  This script is called during the metadata discovery process
  for each event which has been ingested through the email interface
  by portal contributions. It tries to analyse the text content 
  to define the different event parameters.

  This version provides only early support.

  TODO:
  - support forwarded messages
  - support incoming / outgoing messages (in releation with 
    Event_finishIngestion)
"""

getResultValue = context.getPortalObject().portal_catalog.getResultValue
Base_getEntityListFromFromHeader = context.Base_getEntityListFromFromHeader
def getEntityList(text):
  return [entity.getRelativeUrl()
          for entity in Base_getEntityListFromFromHeader(text)]

content_information = context.getContentInformation()
sender_list = context.getSourceList() or getEntityList(content_information.get('From', ''))
to_list = context.getDestinationList() or getEntityList(content_information.get('To', ''))
cc_list = getEntityList(content_information.get('CC', ''))

# Build references
reference_search_list = []
text_search_list = []
for text, prop_dict in context.getSearchableReferenceList():
  if text:
    text_search_list.append(text)
  if 'reference' in prop_dict:
    reference_search_list.append(prop_dict['reference'])

# Search reference ticket or project
follow_up_type_list = context.getPortalProjectTypeList() + context.getPortalTicketTypeList()
follow_up = None
if reference_search_list:
  follow_up = getResultValue(reference=reference_search_list, portal_type=follow_up_type_list)
if follow_up is None and text_search_list:
  follow_up = getResultValue(reference=text_search_list, portal_type=follow_up_type_list)

# Find portal type
subject = content_information.get('Subject', '')
body = context.asText()
portal_type = None
for text in (subject, body):
  portal_type, _ = context.Base_findPortalTypeNameAndMatchedValueForEvent(text)
  if portal_type is not None:
    break

# Build dict.
result = {}
if sender_list:
  result['source_list'] = sender_list
if to_list or cc_list:
  result['destination_list'] = to_list + cc_list
if follow_up is not None:
  result['follow_up'] = follow_up.getRelativeUrl()
if portal_type is not None:
  result['portal_type'] = portal_type

return result
