from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

result = None, None
access_token_document = context
request = context.REQUEST

if access_token_document.getValidationState() == 'validated':
  comment = "Token invalidated but non correctly authentificated"

  if (request["REQUEST_METHOD"] == access_token_document.getUrlMethod()) and \
    (request["ACTUAL_URL"] == access_token_document.getUrlString()):

    agent_document = access_token_document.getAgentValue()
    if agent_document is not None:
      portal = agent_document.getPortalObject()
      for erp5_login in agent_document.objectValues(portal.getPortalLoginTypeList()):
        if erp5_login.getValidationState() == "validated":
          result = erp5_login.getReference(), erp5_login.getPortalType()
      comment = "Token usage accepted"

  access_token_document.invalidate(comment=comment)
return result
