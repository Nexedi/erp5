context.ERP5Site_userFollowUpWebPage(context.getReference())

if context.getReference().startswith("default-"):
  context.setReference(DateTime().millis())

context.share()
base_url = context.getPortalObject().absolute_url()

return "%s/?key=%s" % (base_url, context.getReference())
