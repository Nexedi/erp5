request_efrom = state_change['object']
request_efrom.portal_workflow.doActionFor(M0_Scribus,
                                          'validate_action',
                                          wf_id='form_validation_workflow',
                                          comment=comment or '')
