portal = context.getPortalObject()

# remove the person of the test if existing
person_list = context.Zuite_checkPortalCatalog(portal_type='Person', max_count=1,
                                                      title=context.Zuite_getHowToInfo()['link_howto_person_title'])
if person_list is not None:
  portal.person_module.deleteContent(person_list[0].getId())

# remove the organisation of the test if existing
organisation_list = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=1,
                                                            title=context.Zuite_getHowToInfo()['link_howto_organisation_title'])
if organisation_list is not None:
  portal.organisation_module.deleteContent(organisation_list[0].getId())

# remove the organisation of the test if existing
organisation_list = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=1,
                                                            title=context.Zuite_getHowToInfo()['link_howto_organisation2_title'])
if organisation_list is not None:
  portal.organisation_module.deleteContent(organisation_list[0].getId())

return "Clean Ok"
