query_params = {'delivery.start_date': dict(query=context.getStartDate(), range='max'),
                'portal_type': context.getPortalType(),
                'title': dict(query=context.getTitle(), key='ExactMatch'),
                'simulation_state': ('stopped', 'public_stopped', 'failed'),
                'sort_on': (('delivery.start_date', 'descending'),),}

test_list = context.getParentValue().searchFolder(limit=1, **query_params)
if test_list:
  return test_list[0].getObject()
