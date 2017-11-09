portal = context.getPortalObject()
if portal.portal_skins.updateSkinCookie():
  portal.setupCurrentSkin()
url = REQUEST.get("came_from")
if portal.portal_membership.isAnonymousUser():
  RESPONSE.expireCookie("__ac", path="/")
  url = "%s/login_form?portal_status_message=%s" % (
    context.absolute_url(),
    context.Base_translateString("Login and/or password is incorrect.")
    + ("&amp;came_from=" + url if url else ""))
elif not url:
  url = context.absolute_url()
topmost_url_document = context.Base_getURLTopmostDocumentValue()
if not topmost_url_document.isURLAncestorOf(url):
  return context.ERP5Site_redirect(topmost_url_document.absolute_url(),
    keep_items={'portal_status_message': 'Redirection to an external site prevented.'})
return RESPONSE.redirect(url)
