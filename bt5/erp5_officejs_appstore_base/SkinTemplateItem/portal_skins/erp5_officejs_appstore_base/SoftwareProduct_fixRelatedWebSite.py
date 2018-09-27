portal = context.getPortalObject()

web_site = context.getFollowUpValue(portal_type="Web Section")

# Create Web Site if necessary
if not web_site:
  # XXX Hardcoded templ
  web_site = portal.web_site_module['application-list'].template.Base_createCloneDocument(batch_mode=True)
  web_site.edit(
    title=context.getTitle(),
    short_title=context.getTitle(),
    id=context.getReference().lower(),
  )
  context.setFollowUpValue(web_site)

# This is dangerous
if not web_site.getId() == context.getReference().lower():
  web_site.setId(context.getReference().lower())
if batch_mode:
  return web_site
