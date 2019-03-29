# Make sure there is not any operation wich is not finished yet
# This is usefull when we close a counter date

document_list = context.CounterDate_getRemainingOperationList(site=site)


for document in document_list:
  from Products.ERP5Type.Message import Message
  from Products.DCWorkflow.DCWorkflow import ValidationFailed
  portal_type = document.getTranslatedPortalType()
  reference = document.getSourceReference()
  if reference is None:
    reference = Message(domain='ui',message='Not defined')
  message = Message(domain="ui", 
                message="Sorry, the $portal_type (reference:$reference) is not finished",
                mapping={'portal_type':portal_type,'reference':reference})
  raise ValidationFailed(message)
