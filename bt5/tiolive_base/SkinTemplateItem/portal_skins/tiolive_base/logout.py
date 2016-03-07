"""
  Redirect after logout to TioLive root site.
"""

REQUEST = context.REQUEST
tiolive_site_root_url = context.ERP5Site_getTioLiveSiteRootUrl()
if REQUEST.has_key('portal_skin'):
   context.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
return REQUEST.RESPONSE.redirect(tiolive_site_root_url+'/logged_out')
