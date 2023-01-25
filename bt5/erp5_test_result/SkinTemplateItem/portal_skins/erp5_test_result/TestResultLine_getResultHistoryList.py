"""
Return all previous test result line for the same test, same
test suite, but for older revisions.

Note that creation_date is used, but it could be nicer to use
the start date. However for now it is more convenient from a
catalog point of view
"""

test_result = context.getParentValue()

query_params = {'creation_date' : dict(query=context.getCreationDate(), range='ngt'),
                'portal_type': 'Test Result',
                'limit': limit,
                'title': dict(query=test_result.getTitle(), key='ExactMatch'),
                'simulation_state': ('stopped', 'public_stopped', 'failed'),
                'sort_on': (('creation_date', 'descending'),),}

result_list = []
expected_id = context.getId()
expected_title = context.getTitle()

for tr in context.portal_catalog(**query_params):
  line_found = False
  tr = tr.getObject()

  # Optimisation: the test result line probably have the same id in the previous
  # test result.
  line = getattr(tr, expected_id, None)
  if line is not None and line.getTitle() == expected_title \
      and line.getSimulationState() in ('stopped', 'public_stopped', 'failed'):
    result_list.append(line)
    line_found = True
  else:
    for line in tr.contentValues(portal_type='Test Result Line'):
      if line.getTitle() == context.getTitle() \
         and line.getSimulationState() in ('stopped', 'public_stopped', 'failed'):
        result_list.append(line)
        line_found = True
        # next time, the test result line will likely have the same id as this one.
        expected_id = line.getId()

  # This test result line was not executed in this test. We had a line "Not executed",
  # mainly because we have a count method that counts test results, so we need to
  # return as many test result line as the count method returns.
  if not line_found:
    result_list.append(tr.asContext(string_index='NOT_EXECUTED'))

return result_list
