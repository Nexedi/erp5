portal = context.getPortalObject()
if portal.portal_skins.updateSkinCookie():
  portal.setupCurrentSkin()
url = REQUEST.get("came_from")
if portal.portal_membership.isAnonymousUser():
  RESPONSE.expireCookie("__ac", path="/")
  keep_item_dict = {
    'portal_status_message': context.Base_translateString("Login and/or password is incorrect."),
  }
  if url:
    keep_item_dict['came_from'] = url
  context.Base_redirect(
    form_id='login_form',
    keep_items=keep_item_dict,
  )
  return
if not url:
  url = context.absolute_url()
topmost_url_document = context.Base_getURLTopmostDocumentValue()
if not topmost_url_document.isURLAncestorOf(url):
  return topmost_url_document.Base_redirect(
    keep_items={
      'portal_status_message': context.Base_translateString('Redirection to an external site prevented.'),
    }
  )
return RESPONSE.redirect(url)
