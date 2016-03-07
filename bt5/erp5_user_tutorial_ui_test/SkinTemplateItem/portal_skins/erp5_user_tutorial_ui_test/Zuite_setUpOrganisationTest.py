if clean:
  context.Zuite_tearDownOrganisationTest()

portal = context.getPortalObject()
result_list = portal.portal_catalog(
  portal_type="Organisation",
  title=context.Zuite_getHowToInfo()['organisation_howto_organisation_title'])

if len(result_list) == 0:
  # If you follow the sequence of tutorial, Z Company is already created by previous tutotial.
  # Then, is already expected when running tests from user-Howto.Create.Organisations
  portal.organisation_module.newContent(portal_type="Organisation",
    title=context.Zuite_getHowToInfo()['organisation_howto_organisation_title'])

context.portal_caches.clearAllCache()

return "Init Ok"
