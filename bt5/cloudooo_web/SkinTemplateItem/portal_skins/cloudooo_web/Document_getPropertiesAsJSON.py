#try:         //Implement try catch instead of if else
#from Products.ERP5Type.JSON import dumps
from Products.ERP5Type.JSONEncoder import encodeInJson as dumps

portal = context.getPortalObject()
reference = portal.portal_membership.getAuthenticatedMember().getIdOrUserName()
processing = None

if reference == "Anonymous User":
  processing = "anonymous_user"
else:
  session = portal.portal_sessions[reference]
  document_url = session.get('document_url',None)
  if document_url is None:
    processing = "document_url_error"
  else:
    document = portal.restrictedTraverse(document_url)

  try:
    processing = document.getExternalProcessingState()
  except AttributeError:
    processing = 'empty'

informations = { 'processing': processing,
                  'reference': reference  }

if informations['processing'] in ['converted', 'conversion_failed','empty']:
  informations['permanent_url'] = document.Document_getPermanentUrl()
  print(dumps(informations)) #print info before del object
  portal.portal_sessions.manage_delObjects(reference)
else:
  print(dumps(informations))

return printed
