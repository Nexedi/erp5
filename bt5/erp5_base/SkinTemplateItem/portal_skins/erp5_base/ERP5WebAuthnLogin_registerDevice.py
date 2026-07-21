import json

webauthn_login = context

webauthn_login.finishRegistration(
  challenge=challenge,
  public_key_credential=json.loads(public_key_credential_json),
  relying_party_id=context.REQUEST.getHeader('Host', None),
  http_origin=context.REQUEST.getHeader('Origin', None),
)

return webauthn_login.Base_redirect()
