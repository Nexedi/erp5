portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()

# remove the person of the test if existing
person_list = context.portal_catalog(portal_type='Person',
                                     title=(howto_dict['person_howto_title'], howto_dict['person_howto_title2'],))
if person_list is not None:
  portal.person_module.deleteContent([x.getId() for x in person_list])

# remove the organisation of the test if existing
organisation_list = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=1,
                                                     title=howto_dict['person_howto_organisation_title'])
if organisation_list is not None:
  portal.organisation_module.deleteContent(organisation_list[0].getId())

return "Clean Ok"
