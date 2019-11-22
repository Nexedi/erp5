import json

absolute_url = context.absolute_url()
request_url = "%s/SupportRequestModule_viewLastSupportRequestListAsRss" % (absolute_url,)
portal = context.getPortalObject()
person = portal.portal_membership.getAuthenticatedMember().getUserValue()

if person is None:
  return json.dumps({'restricted_access_url': request_url})

access_token = None

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

url = "%s?access_token=%s&access_token_secret=%s" % (
        request_url,
        access_token.getId(),
        reference)

return json.dumps({'restricted_access_url': url})
