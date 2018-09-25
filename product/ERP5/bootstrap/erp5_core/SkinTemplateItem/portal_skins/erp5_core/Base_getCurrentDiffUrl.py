"""
This URL script is used for Historical comparison list
to show the diff between the new value and current value.

In case there new value is the current value, there is no
need to show the diff link.
"""
request = context.REQUEST

# In this case, the second serial should be the current value, i.e, 0.0.0.0
first_serial = getattr(brain, 'next_serial', '0.0.0.0')
second_serial = '0.0.0.0'
time = getattr(brain, 'time', '')
action = getattr(brain, 'action', '')
actor = getattr(brain, 'actor', '')

# There is no need to compare revisions in case its the
# first version.
if first_serial != second_serial:
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

  return 'Base_viewHistoricalComparisonDiff?first_serial=%s&amp;second_serial=%s&amp;time=%s&amp;action=%s&amp;actor=%s'\
      % ( first_serial, second_serial, time, action, actor )

elif url_dict:
  return {}
