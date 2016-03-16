if clean:
  context.Zuite_tearDownFullTextSearchTest()

portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()


person = portal.person_module.newContent(portal_type='Person',
                                         title=howto_dict['full_text_person_title'],
                                         reference=howto_dict['full_text_person_reference'],
                                         default_email_text=howto_dict['full_text_person_email'])
# create Organisation
organisation = portal.organisation_module.newContent(portal_type='Organisation',
                                                     title=howto_dict['full_text_organisation_title'],
                                                     default_email_text=howto_dict['full_text_organisation_email'])
# set organisation
person.setCareerSubordinationValue(organisation)

# Create Currency
portal.currency_module.newContent(portal_type='Currency',
                                  title=howto_dict['dig_currency_title'])

return "Init Ok"
