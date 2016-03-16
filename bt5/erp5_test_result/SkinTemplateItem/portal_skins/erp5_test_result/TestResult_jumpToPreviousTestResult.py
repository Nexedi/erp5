previous_test = context.TestResult_getPrevious()
if previous_test is None:
  message = 'No Previous Test Result'
else:
  context = previous_test
  message = 'Previous Test Result'

redirect = container.REQUEST.RESPONSE.redirect
from ZTUtils import make_query
return redirect('%s/%s?%s' % (
                context.absolute_url_path(),
                form_id, make_query(selection_name=selection_name,
                                    selection_index=selection_index,
                                    portal_status_message=message)))
