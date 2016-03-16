'''
  This script generate some web page name related to the context
  ex :
  DeclarationTVA-Draft-PDFDocument_viewAttachmentList-Upload.Button-Citizen
'''

# get some information about the context
absolute_url = context.getAbsoluteUrl()
portal_type = context.getPortalType()
request = context.REQUEST
form_id = request.get('form_id', None)

# remove spaces
portal_type = portal_type.replace(' ', '')
id = context.getId()

web_page_name = []
web_page_name.append(portal_type)
if getattr(context, 'getValidationState', None) and context.getValidationState():
  web_page_name.append(context.getValidationState())

if form_id:
  web_page_name.append(form_id)

web_site_id = context.getWebSiteValue().getId()
if web_site_id == 'egovernment':
  web_page_name.append('Agent')
if web_site_id == 'ecitizen':
  web_page_name.append('Citizen')

return '-'.join(web_page_name)
