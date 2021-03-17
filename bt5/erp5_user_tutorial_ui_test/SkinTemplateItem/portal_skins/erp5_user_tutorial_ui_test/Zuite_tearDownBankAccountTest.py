portal = context.getPortalObject()

# remove the organisation of the test if existing
organisation_list = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=1,
                                                     title=context.Zuite_getHowToInfo()['organisation_howto_organisation_title'])
bank_account_list = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=1,
                                                     title=context.Zuite_getHowToInfo()['bankaccount_howto_organisation_title'])

if organisation_list is not None:
  # Z Company itself
  portal.organisation_module.deleteContent(organisation_list[0].getId())

if bank_account_list is not None:
  # The bank account created by the test
  portal.organisation_module.deleteContent(bank_account_list[0].getId())

return "Clean Ok"
