import base64
import json

portal = context.getPortalObject()

def decode_jwt_no_verify(token):
  parts = token.split('.')
  if len(parts) != 3:
    raise ValueError("Invalid JWT: should have 3 parts")
  _, payload_b64, _ = parts
  def base64url_decode(b64_string):
    padding = '=' * (-len(b64_string) % 4)
    return base64.urlsafe_b64decode(b64_string + padding)

  payload_json = base64url_decode(payload_b64)
  return json.loads(payload_json)

if token:
  jwt = decode_jwt_no_verify(token)
  user_name = jwt["upn"].split("@")[0].lower()

module = context.getPortalObject().getDefaultModule(portal_type='Credential Request')
credential_request = module.newContent(
  portal_type="Credential Request",
  first_name=user_name,
  reference=user_dict["sub"],
)

credential_request.submit()
context.portal_alarms.accept_submitted_credentials.activeSense()
