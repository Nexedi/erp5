portal = context.getPortalObject()
if portal.portal_skins.updateSkinCookie():
  portal.setupCurrentSkin()
came_from = REQUEST.get("came_from")
if portal.portal_membership.isAnonymousUser():
  RESPONSE.expireCookie("__ac", path="/")
  parameter_dict = {'portal_status_message': context.Base_translateString("Login and/or password is incorrect.")}
  if came_from:
    parameter_dict['came_from'] = came_from
  url = context.Base_constructUrlFor(
    form_id='login_form',
    parameter_dict=parameter_dict
  )
elif came_from:
  url = came_from
else:
  url = context.Base_constructUrlFor()
topmost_url_document = context.Base_getURLTopmostDocumentValue()
if not topmost_url_document.isURLAncestorOf(url):
  return context.ERP5Site_redirect(topmost_url_document.Base_constructUrlFor(),
    keep_items={'portal_status_message': 'Redirection to an external site prevented.'})
return RESPONSE.redirect(url)
