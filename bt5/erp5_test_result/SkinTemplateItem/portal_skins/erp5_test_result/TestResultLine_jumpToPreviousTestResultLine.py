test_result = context.getParentValue()
test_result_module = test_result.getParentValue()

query_params = {'delivery.start_date': dict(query=test_result.getStartDate(), range='max'),
                'portal_type': test_result.getPortalType(),
                'title': dict(query=test_result.getTitle(), key='ExactMatch'),
                'simulation_state': 'stopped',
                'sort_on': (('delivery.start_date', 'descending'),),}

test_list = test_result_module.searchFolder(**query_params)

redirect = container.REQUEST.RESPONSE.redirect
from ZTUtils import make_query
if test_list:
  previous_test_result = test_list[0].getObject()
  test_case_list = [tc for tc in previous_test_result.contentValues() if tc.getTitle() == context.getTitle()]
  if test_case_list:
    return redirect('%s/%s?%s' % (
                  test_case_list[0].absolute_url(),
                  form_id, make_query(selection_name=selection_name,
                                      selection_index=selection_index,
                                      portal_status_message='Previous Test Result Line')))

return redirect('%s/%s?%s' % (
                context.absolute_url(),
                form_id, make_query(selection_name=selection_name,
                                    selection_index=selection_index,
                                    portal_status_message='No Previous Test Result Line')))
