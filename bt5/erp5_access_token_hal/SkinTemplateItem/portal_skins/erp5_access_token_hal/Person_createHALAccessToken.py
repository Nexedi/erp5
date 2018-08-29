from DateTime import DateTime
portal = context.getPortalObject()

token = portal.access_token_module.newContent(
  id='%s-%s' % (DateTime().strftime('%Y%m%d'), portal.Base_generateAccessTokenHalID()),
  portal_type='HAL Access Token',
  agent_value=context
)
token.validate()
return token
