from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed

# Check that a check exists for given bank account and reference.
if check is None:
  check = context.Base_checkOrCreateCheck(reference=reference, 
                                         bank_account=bank_account,
                                         resource=resource)

bad_simulation_state_dict = {'draft': 'The check is not issued yet.',
                             'cancelled': 'The check has been stopped.',
                             'delivered': 'The check has already been cashed.',
                             'stopped': 'The check is stopped.'}

simulation_state = check.getSimulationState()
if simulation_state != 'confirmed':
  if simulation_state in bad_simulation_state_dict:
    msg = Message(domain='ui', message=bad_simulation_state_dict[simulation_state])
  else:
    msg = 'Invalid and unhandled simulation state: %s' % (simulation_state, )
  raise ValidationFailed(msg,)

return check
