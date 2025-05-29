"""
This URL script is used for Historical comparison list.
There are two cases handled here. If it is the first
row of the list(having serial as 0.0.0.0), then we don't
want to have any URL as there is no comparison needed,
thus we return empty dictionary in case of renderJS UI and
nothing for XHTMl UI.
"""
from ZTUtils import make_query

request = container.REQUEST

serial = getattr(brain, 'serial', '0.0.0.0')
next_serial = getattr(brain, 'next_serial', '0.0.0.0')
time = getattr(brain, 'time', '')
action = getattr(brain, 'action', '')
actor = getattr(brain, 'actor', '')

# There is no need to compare revisions in case its the
# first version.
if serial != '0.0.0.0':
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
              'view': 'view_historical_comparison',
              'jio_key': request.get('relative_url'),
              'extra_param_json': {
                'serial': serial,
                'next_serial': next_serial,
                'time': time,
                'action': action,
                'actor': actor,
              }
            }
           }

  query_kw = {
    'serial': serial,
    'next_serial': next_serial,
    'time': time,
    'action': action,
    'actor': actor
  }
  ignore_layout = request.get('ignore_layout')
  if ignore_layout is not None:
    query_kw['ignore_layout'] = ignore_layout
  return 'Base_viewHistoricalComparison?%s' % make_query(query_kw)

elif url_dict:
  return {}
