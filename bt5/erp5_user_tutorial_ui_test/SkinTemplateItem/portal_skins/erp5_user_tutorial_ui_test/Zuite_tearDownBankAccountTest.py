portal = context.getPortalObject()

# remove the organisation of the test if existing
organisation_list = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=2)

if organisation_list is not None:
  # Z Company itself
  portal.organisation_module.deleteContent(organisation_list[0].getId())
  # The bank account created by the test
  portal.organisation_module.deleteContent(organisation_list[1].getId())

return "Clean Ok"
