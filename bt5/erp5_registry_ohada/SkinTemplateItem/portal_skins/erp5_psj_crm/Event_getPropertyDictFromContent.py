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

def getPersonList(information_text):
  result = []
  for recipient in information_text.split(','):
    if "<" in recipient:
      recipient = recipient[recipient.find('<') + 1:]
      recipient = recipient[:recipient.find('>')]
    if recipient:
      email = getResultValue(url_string=recipient, portal_type="Email")
      if email is not None:
        result.append(email.getParentValue().getRelativeUrl())
  return result

content_information = context.getContentInformation()
sender_list = getPersonList(content_information.get('From', ''))
to_list = getPersonList(content_information.get('To', ''))
cc_list = getPersonList(content_information.get('CC', ''))

# Build references
reference_search_list = []
text_search_list = []
for text, prop_dict in context.getSearchableReferenceList():
  if text:
    text_search_list.append(text)
  if prop_dict.has_key('reference'):
    reference_search_list.append(prop_dict['reference'])

# Search reference ticket or project
follow_up_type_list = context.getPortalProjectTypeList() + context.getPortalTicketTypeList()
follow_up = None
if reference_search_list:
  follow_up = getResultValue(reference=reference_search_list, portal_type=follow_up_type_list)
if follow_up is None and text_search_list:
  follow_up = getResultValue(reference=text_search_list, portal_type=follow_up_type_list)

# Build dict.
result = {}
if sender_list:
  result['source_list'] = sender_list
if to_list or cc_list:
  result['destination_list'] = to_list + cc_list
if follow_up is not None:
  result['follow_up'] = follow_up.getRelativeUrl()

return result
