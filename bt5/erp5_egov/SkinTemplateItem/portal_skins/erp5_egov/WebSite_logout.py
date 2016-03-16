"""
  Default logout handler, overwritten to give website specific portal status message.
"""
portal = context.getPortalObject()
N_ = portal.Base_translateString
website = context.getWebSiteValue()
form_id='EGov_viewLoginForm'

REQUEST = context.REQUEST
if REQUEST.has_key('portal_skin'):
   context.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
msg = N_('You have been logged out. Thank you for using this website.')
return website.Base_redirect(form_id, keep_items = {'portal_status_message' : msg},
                             editable_mode=editable_mode, **kw)
