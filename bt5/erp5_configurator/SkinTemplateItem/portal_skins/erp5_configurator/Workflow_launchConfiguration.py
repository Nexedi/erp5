portal = context.getPortalObject()
request = context.REQUEST
bc = context.business_configuration_module.newContent(
  resource=context.getRelativeUrl(),
  title=title,
)

request.set("field_your_business_configuration", bc.getRelativeUrl())

# Configurator use a cookie to know what's the "current" configuration,
# we also need to initialize this cookie (yes, this is a ugly)
request.RESPONSE.setCookie(
  'business_configuration_key',
  bc.getRelativeUrl(),
  path=portal.portal_configurator.absolute_url_path()
)

return portal.portal_configurator.login(REQUEST=request)
