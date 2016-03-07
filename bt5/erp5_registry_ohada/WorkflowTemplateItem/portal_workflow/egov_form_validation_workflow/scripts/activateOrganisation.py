request_eform = state_change['object']
portal = request_eform.getPortalObject()
rccm =request_eform.getReference()
result_list = portal.portal_catalog(parent_uid=portal.organisation_module.getUid(),
                                    reference=rccm)
for object in result_list:
  organisation_module = portal.organisation_module
  login = object.getId()
  org = organisation_module[login]
  org.Base_DoWorkflowAction(action_name = 'activer_entreprise_action',
                            wf_id = 'business_life_cycle_workflow')

return 'Organisation Updated'
