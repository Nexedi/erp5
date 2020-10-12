"""
Return the list of unread acknowledgements for the  user currently
connected. This script will use efficiently caches in order to slow
down as less a possible the user interface
"""
from DateTime import DateTime
portal = context.getPortalObject()

user_name = portal.portal_membership.getAuthenticatedMember().getId()

def getUnreadAcknowledgementListForUser(user_name=None):
  # We give the portal type "Mass Notification" for now, we can
  # have a getPortalAcknowledgeableTypeList method in the future
  portal_acknowledgements = getattr(portal, "portal_acknowledgements", None)
  result = []
  if portal_acknowledgements is not None:
    result = context.portal_acknowledgements.getUnreadDocumentUrlList(
              user_name=user_name, portal_type="Site Message")
  return result

from Products.ERP5Type.Cache import CachingMethod

# Cache for every user the list of url of not acknowledge documents
getUnreadAcknowledgementList = CachingMethod(getUnreadAcknowledgementListForUser,
                                        "getUnreadAcknowledgementListForUser")
return_list = []
url_list = getUnreadAcknowledgementList(user_name=user_name)
# For every not acknowledge document, check that documents are still not
# acknowledged and return them for the user interface
if len(url_list) > 0:
  acknowledgement_list = portal.portal_acknowledgements.getUnreadAcknowledgementList(
		  url_list=url_list, user_name=user_name)
  for acknowledgement in acknowledgement_list:
    #bulletin = acknowledgement.getCausalityValue()
    #event = bulletin.getFollowUpRelatedValue()
    text_content = acknowledgement.getTextContent()
    return_list.append({
	  "title": acknowledgement.getTitle(),
	  "text_content": text_content,
	  "acknowledge_url": "AcknowledgementTool_acknowledge?acknowledgement_url=%s" % \
             acknowledgement.getCausality()})

return return_list
