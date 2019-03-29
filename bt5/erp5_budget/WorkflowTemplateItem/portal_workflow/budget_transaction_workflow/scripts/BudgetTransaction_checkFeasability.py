from Products.DCWorkflow.DCWorkflow import ValidationFailed

object = state_change['object']
error_msg = 'Please correct the following errors:'

consistency = object.checkConsistency()
for elem in consistency:
  error_msg =error_msg+' '+elem[4]

if consistency != []:
  raise ValidationFailed(str(error_msg))
