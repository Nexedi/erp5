portal = context.getPortalObject()
howto_dict = portal.Zuite_getHowToInfo()

# delete Person
person_list = portal.portal_catalog(portal_type='Person',
                                    title=howto_dict['full_text_person_title'],
                                    reference=howto_dict['full_text_person_reference'],
                                    local_roles='Owner')
if person_list:
  portal.person_module.manage_delObjects([person_list[0].getObject().getId()])

# delete Organisation
organisation_list = portal.portal_catalog(portal_type='Organisation',
                                          title=howto_dict['full_text_organisation_title'],
                                          local_roles='Owner')
if organisation_list:
  portal.organisation_module.manage_delObjects([organisation_list[0].getObject().getId()])

# delete Currency
currency = portal.portal_catalog.getResultValue(portal_type='Currency',
                                                title=howto_dict['dig_currency_title'],
                                                local_roles='Owner')

if currency is not None:
  portal.currency_module.deleteContent(currency.getId())

return "Clean Ok"
