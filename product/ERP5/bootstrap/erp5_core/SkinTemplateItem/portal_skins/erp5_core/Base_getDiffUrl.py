"""
This URL script is used for Historical comparison list
to get diff between old and new value
"""
from ZTUtils import make_query

request = container.REQUEST

first_serial = getattr(brain, 'serial', '0.0.0.0')
second_serial = getattr(brain, 'next_serial', '0.0.0.0')
time = getattr(brain, 'time', '')
action = getattr(brain, 'action', '')
actor = getattr(brain, 'actor', '')

# There is no need to compare revisions in case its the
# first version.
if url_dict:
  return {'command': 'index',
          'options': {
            # XXX: This shouldn't be the referred way to get
            # relative URL, but if we directly use context here
            # to get the relative URL, it will return us the
            # URL of tempbase object of list, which is not
            # what we desire, thus taking the approach to
            # get it via REQUEST
            'jio_key': request.get('relative_url'),
          },
          'view_kw': {
            'view': 'view_historical_diff',
            'jio_key': request.get('relative_url'),
            'extra_param_json': {
              'first_serial': first_serial,
              'second_serial': second_serial,
              'time': time,
              'action': action,
              'actor': actor,
            }
          }
         }

query_kw = {
  'first_serial': first_serial,
  'second_serial': second_serial,
  'time': time,
  'action': action,
  'actor': actor
}
ignore_layout = request.get('ignore_layout')
if ignore_layout is not None:
  query_kw['ignore_layout'] = ignore_layout
return 'Base_viewHistoricalComparisonDiff?%s' % make_query(query_kw)
