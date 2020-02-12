SUPPORT_ENABLED = 'support_enabled'
SUPPORT_DISABLED = 'support_disabled'

if express_mode==SUPPORT_ENABLED:
  # For Express users.
  proxy_path = 'web_site_module/express_frame/WebSite_viewExpressCustomerSupportMenu'
elif express_mode==SUPPORT_DISABLED:
  return ''
else:
  # Advertisement
  # XXXX FIX THIS URL!!!
  proxy_path = 'web_site_module/express_frame/WebSite_viewDummyAdvertisement'


# XXX we need to think about https
traverse_subpath = proxy_path.split('/')
context.REQUEST.set('traverse_subpath', traverse_subpath)
return context.portal_wizard.proxy()
