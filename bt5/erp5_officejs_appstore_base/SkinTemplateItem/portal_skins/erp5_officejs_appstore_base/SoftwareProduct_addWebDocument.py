portal = context.getPortalObject()
module = portal.getDefaultModule(portal_type)

document = module.newContent(
  portal_type=portal_type,
  reference=reference,
  title=title,
  follow_up=context.getRelativeUrl(),
)

return document.Base_redirect(
  '',
  keep_items={
    'portal_status_message': portal.Base_translateString("Web Document Created"),
  }
)
