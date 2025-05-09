portal = context.getPortalObject()
translateString = portal.Base_translateString
previous_test = context.TestResult_getPrevious()

if previous_test is None:
  message = 'No Previous Test Result'
  level = 'error'
else:
  context = previous_test
  message = 'Previous Test Result'
  level = 'success'

return context.Base_redirect(
  form_id,
  keep_items={
    'portal_status_message': translateString(message),
    'portal_status_level': level,
  }
)
