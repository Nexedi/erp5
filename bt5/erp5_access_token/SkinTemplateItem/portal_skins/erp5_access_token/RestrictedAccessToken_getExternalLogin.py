from zExceptions import Unauthorized
import hmac
if REQUEST is not None:
  raise Unauthorized

access_token_document = context
request = context.REQUEST

if access_token_document.getValidationState() == 'validated':

  if (request["REQUEST_METHOD"] == access_token_document.getUrlMethod()) and \
    (request["ACTUAL_URL"] == access_token_document.getUrlString()):

    reference = request.getHeader("X-ACCESS-TOKEN-SECRET", None)
    if reference is None:
      reference = request.form.get("access_token_secret", "INVALID_REFERERENCE")

    # use hmac.compare_digest and not string comparison to avoid timing attacks
    if not hmac.compare_digest(access_token_document.getReference(), reference):
      return None, None

    agent_document = access_token_document.getAgentValue()
    if agent_document is not None:
      portal = agent_document.getPortalObject()
      for erp5_login in agent_document.objectValues(portal.getPortalLoginTypeList()):
        if erp5_login.getValidationState() == "validated":
          return erp5_login.getReference(), erp5_login.getPortalType()

return None, None
