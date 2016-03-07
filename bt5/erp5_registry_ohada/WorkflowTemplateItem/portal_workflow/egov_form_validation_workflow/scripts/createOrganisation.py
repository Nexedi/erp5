request_eform = state_change['object']
portal = request_eform.getPortalObject()
organisation_module = portal.organisation_module
denomination = request_eform.getTitle()
name = request_eform.getName()
rccm =request_eform.getReference()
address = request_eform.getAddress()
place = request_eform.getDefaultAddressCity()

ORGANISATION_DATA = ( ( denomination, name, rccm ,address, place),)

for login, corporate_name, reference,default_address_street_address, default_address_city in ORGANISATION_DATA:
  if login in organisation_module.objectIds():
    organisation = organisation_module[login]
  else:
    organisation = organisation_module.newContent(id=login,
                                                  portal_type='Organisation')

  organisation.edit(title = login,
                    corporate_name = corporate_name,
                    reference = reference,
                    default_address_street_address = default_address_street_address,
                    default_address_city = default_address_city,)

organisation.Base_DoWorkflowAction(action_name = 'deposer_dossier_action',
                                   wf_id = 'business_life_cycle_workflow')

return 'Organisations Created.'
