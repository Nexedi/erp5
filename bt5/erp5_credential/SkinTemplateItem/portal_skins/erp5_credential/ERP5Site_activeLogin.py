from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

assert key
mail_message = portal.portal_catalog.getResultValue(portal_type="Mail Message", reference=key)

credential_request = mail_message.getFollowUpValue()
if credential_request.getValidationState() in ('submitted', 'accepted'):
  message = translateString("Your account is already active.")
else:
  credential_request.submit(comment=translateString('Created by subscription form'))
  mail_message.deliver()
  message = translateString("Your account is being activated. You will receive an e-mail when activation is complete.")

return context.Base_redirect("login_form", keep_items=dict(portal_status_message=message))
