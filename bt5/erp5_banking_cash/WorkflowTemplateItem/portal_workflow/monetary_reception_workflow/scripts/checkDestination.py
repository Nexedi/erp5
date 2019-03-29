from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed

object = state_change['object']

# use of the constraint
vliste = object.checkConsistency()
object.log('vliste', vliste)
if len(vliste) != 0:
  raise ValidationFailed(vliste[0].getMessage(),)


# first check if we have line defined
if len(object.objectValues(portal_type='Cash Delivery Line')) == 0:
  msg = Message(domain="ui", message="No line defined on document.")
  raise ValidationFailed(msg,)
       
dest = object.getDestinationValue()
if dest is None or 'encaisse_des_billets_retires_de_la_circulation' in dest.getRelativeUrl():
  msg = Message(domain="ui", message="Wrong Destination Selected.")
  raise ValidationFailed(msg,)

# check again that we are in the good accounting date
object.Baobab_checkCounterDateOpen(site=dest, date=object.getStartDate())


# check between letter and destination site codification
# Make sure objects are Banknotes
if 'transit' not in dest.getRelativeUrl():
  first_movement = object.Delivery_getMovementList(portal_type=['Cash Delivery Line','Cash Delivery Cell'])[0]
  if first_movement.getResourceValue().getPortalType()=='Banknote':
    line_letter = first_movement.getEmissionLetter()
    if line_letter.lower() != dest.getCodification()[0].lower():
      msg = Message(domain="ui", message="Letter defined on line do not correspond to destination site.")
      raise ValidationFailed(msg,)
