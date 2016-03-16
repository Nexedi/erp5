"""Count all previous test result line for the same test, same
test suite, but for older revisions.
"""

test_result = context.getParentValue()
query_params = {'portal_type': 'Test Result',
                'title': dict(query=test_result.getTitle(), key='ExactMatch'),
                'simulation_state': ('stopped', 'public_stopped', 'failed'),
                }
return context.portal_catalog.countResults(**query_params)
