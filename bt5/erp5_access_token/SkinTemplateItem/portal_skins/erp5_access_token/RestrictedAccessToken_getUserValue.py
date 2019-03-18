from zExceptions import Unauthorized
import hmac
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

    # use hmac.compare_digest and not string comparison to avoid timing attacks
    if not hmac.compare_digest(access_token_document.getReference(), reference):
      return None

    agent_document = access_token_document.getAgentValue()
    if agent_document is not None:
      if agent_document.getPortalType() == 'Person':
        # if this is a token for a person, only make accept if person has valid
        # assignments and a validated login (for compatibility with login/password
        # authentication)
        if agent_document.getValidationState() == 'deleted':
          return None
        now = DateTime()
        for assignment in agent_document.contentValues(portal_type='Assignment'):
          if assignment.getValidationState() == "open" and (
              not assignment.hasStartDate() or assignment.getStartDate() <= now
            ) and (
              not assignment.hasStopDate() or assignment.getStopDate() >= now
            ):
            break
        else:
          return None

        user, = context.getPortalObject().acl_users.searchUsers(
            exact_match=True,
            id=agent_document.Person_getUserId())
        if not user['login_list']:
          return None

      result = agent_document

return result
