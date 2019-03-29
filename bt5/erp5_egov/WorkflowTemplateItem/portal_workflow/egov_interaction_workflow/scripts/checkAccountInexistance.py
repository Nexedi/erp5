changed_object = state_change['object']
translateString = changed_object.Base_translateString
login = changed_object.getCompanyName().lower()
portal_catalog = changed_object.portal_catalog
ninea = changed_object.getCompanyNineaNumber()

# check that no existing organisation have the same NINEA number or login
from Products.DCWorkflow.DCWorkflow import ValidationFailed

result = portal_catalog(portal_type='Organisation', vat_code=ninea)

if len(result) > 1:
  msg = "Error : There is more than one company with the NINEA code ${code}"
  msg = translateString(msg, mapping=dict(code=ninea))
  raise ValidationFailed(msg) 

if len(result) == 1 and result[0].getObject().getReference():
  msg = "Error : A company with the NINEA code ${code} already exists and have already an account"
  msg = translateString(msg, mapping=dict(code=ninea))
  raise ValidationFailed(msg)
