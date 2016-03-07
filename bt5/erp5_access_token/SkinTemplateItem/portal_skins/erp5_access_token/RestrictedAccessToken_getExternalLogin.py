from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

result = None
access_token_document = context
request = context.REQUEST

if access_token_document.getValidationState() == 'validated':

  if (request["REQUEST_METHOD"] == access_token_document.getUrlMethod()) and \
    (request["ACTUAL_URL"] == access_token_document.getUrlString()):

    reference = request.getHeader("X-ACCESS-TOKEN-SECRET", None)
    if reference is None:
      reference = request.form.get("access_token_secret", "INVALID_REFERERENCE")
  
    if access_token_document.getReference() != reference:
      return None
    
    agent_document = access_token_document.getAgentValue()
    if agent_document is not None:
      result = agent_document.getReference(None)

return result
