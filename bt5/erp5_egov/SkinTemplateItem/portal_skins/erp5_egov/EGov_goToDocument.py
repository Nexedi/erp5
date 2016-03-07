portal = context.getPortalObject()
N_ = portal.Base_translateString

if not application_number and id:
  application_number = id

keep_items = {}

# default view is history view
form_id='PDFDocument_viewHistory'

if application_number:
  document = context.portal_catalog.getResultValue(id=application_number)
  state = document.getValidationState()
  if document is not None:
    if state == 'draft':
      form_id='view'
    else:
      form_id='PDFDocument_viewHistory'
    return document.Base_redirect(form_id=form_id, keep_items=keep_items)

# Prepare message
msg = N_('Sorry, this document is not available')
return context.Base_redirect(form_id='view', keep_items = {'portal_status_message' : msg})
