from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

result = None, None
access_token_document = context
request = context.REQUEST
portal = context.getPortalObject()

if access_token_document.getValidationState() == 'validated':
  if (portal.portal_skins.getCurrentSkinName() == 'HalRestricted'):

    agent_document = access_token_document.getAgentValue()
    if agent_document is not None:
      for erp5_login in agent_document.objectValues(portal.getPortalLoginTypeList()):
        if erp5_login.getValidationState() == "validated":
          result = erp5_login.getReference(), erp5_login.getPortalType()

return result
