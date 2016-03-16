if clean:
  context.Zuite_tearDownPersonAndOrganisationLinkingTest()

portal = context.getPortalObject()
person = portal.person_module.newContent(portal_type='Person',
                                         first_name=context.Zuite_getHowToInfo()['link_howto_person_first_name'],
                                         last_name=context.Zuite_getHowToInfo()['link_howto_person_last_name'])
person.validate()

organisation = portal.organisation_module.newContent(portal_type='Organisation',
                                                     title=context.Zuite_getHowToInfo()['link_howto_organisation_title'],
                                                     corporate_name=context.Zuite_getHowToInfo()['link_howto_organisation_title'])
organisation.validate()

portal.portal_caches.clearAllCache()

return "Init Ok"
