from Products.DCWorkflow.DCWorkflow import ValidationFailed

request_eform = state_change['object']
if not (request_eform.getMoralPerson() or request_eform.getBranch() or request_eform.getSecondCompany()):
  raise ValidationFailed('Role for the organisation has not been defined, you cannot validate it')
