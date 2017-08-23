from zExceptions import Unauthorized
import json

absolute_url = context.absolute_url()
href = "SupportRequestModule_viewLastSupportRequestListAsRss"
portal = context.getPortalObject()
person = portal.ERP5Site_getAuthenticatedMemberPersonValue()

if person is None:
  raise Unauthorized("You must logged in first!")

access_token = None

request_url = "%s/%s" % (absolute_url, href)

for token_item in portal.portal_catalog(
  portal_type="Restricted Access Token",
  default_agent_uid=person.getUid(),
  validation_state='validated'
  ):
  if token_item.getUrlString() == request_url:
    access_token = token_item
    reference = access_token.getReference()
    break

if access_token is None:
  access_token = portal.access_token_module.newContent(
    portal_type="Restricted Access Token",
    url_string=request_url,
    url_method="GET",
  )
  access_token.setAgentValue(person)
  reference = access_token.getReference()
  access_token.validate()

url = "%s/%s?portal_skin=RSS&access_token=%s&access_token_secret=%s" % (
        absolute_url,
        href,
        access_token.getId(),
        reference)

return json.dumps({'restricted_access_url': url})
