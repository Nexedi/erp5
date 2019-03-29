from Products.DCWorkflow.DCWorkflow import ValidationFailed
current_object = context.getObject()
assignment_list = current_object.getDestinationFormRelatedValueList()
for assignment in assignment_list:
  if current_object.getPortalType()=='M0':
    legal_form = current_object.getLegalForm().lower()
  elif current_object.getPortalType()=='M2':
    legal_form = current_object.getNewLegalForm().lower()
  else:
    portal = context.getPortalObject()
    rccm = current_object.getCorporateRegistrationCode()
    pers_result = context.ERP5RegistryOhada_getRelatedPersonList()
    if len(pers_result) < 1:
      raise ValidationFailed('There is no Person corresponding to the corporate registration code %s' % rccm)
    person = pers_result[0].getObject()
    #legal_form = person.getSocialForm()
  if assignment.getFunction()=='entreprise/associe' :
    if legal_form == 'gie':
      assignment.getFunctionValue().setTitle('Membre du GIE')
    elif legal_form == 'sarl':
      assignment.getFunctionValue().setTitle('Associé de SARL')
    elif legal_form == 'sa': 
      assignment.getFunctionValue().setTitle('Actionnaire de SA')

return assignment_list
