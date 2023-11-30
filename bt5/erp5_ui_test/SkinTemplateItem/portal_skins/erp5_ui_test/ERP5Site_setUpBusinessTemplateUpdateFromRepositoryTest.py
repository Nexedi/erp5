portal = context.getPortalObject()
bt = portal.portal_templates.newContent(
  title='test_core',
)
bt.install()
return 'OK'
