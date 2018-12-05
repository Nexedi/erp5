portal = context.getPortalObject()
request = context.REQUEST
bc = context.business_configuration_module.newContent(
  resource=context.getRelativeUrl(),
  title=title,
)

request.set("field_your_business_configuration", bc.getRelativeUrl())

return portal.portal_configurator.login(REQUEST=request)
