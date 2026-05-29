"""Return RSS feed URL with Restricted Access Token parameters if available.

For authenticated users with token creation permission, generates or reuses
a Restricted Access Token bound to the RSS endpoint URL. For anonymous users
or those without permission, returns the plain RSS URL.
"""
from ZTUtils import make_query

portal = context.getPortalObject()
person = portal.ERP5Site_getAuthenticatedMemberPersonValue()
rss_script = "DiscussionForum_viewLatestPostListAsRSS"
absolute_url = context.absolute_url()
request_url = "%s/%s" % (absolute_url, rss_script)

if person is None or not context.Base_checkPermission(
    'access_token_module', 'Add portal content'):
  return "%s?%s" % (request_url, make_query({'portal_skin': 'RSS'}))

# Search for existing validated token for this exact URL
access_token = None
for token_item in portal.portal_catalog(
    portal_type="Restricted Access Token",
    default_agent_uid=person.getUid(),
    validation_state='validated'):
  if token_item.getUrlString() == request_url:
    access_token = token_item
    break

if access_token is None:
  access_token = portal.access_token_module.newContent(
    portal_type="Restricted Access Token",
    url_string=request_url,
    url_method="GET",
  )
  access_token.setAgentValue(person)

if access_token.getValidationState() == 'draft':
  access_token.validate()

return "%s?%s" % (request_url, make_query({
  'portal_skin': 'RSS',
  'access_token': access_token.getId(),
  'access_token_secret': access_token.getReference(),
}))
