"""
This URL script is used for Historical comparison list
to get diff between old and new value
"""
request = context.REQUEST

serial = getattr(brain, 'serial', '0.0.0.0')
next_serial = getattr(brain, 'next_serial', '0.0.0.0')
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
              'first_serial': serial,
              'second_serial': next_serial,
              'time': time,
              'action': action,
              'actor': actor,
            }
          }
         }

return 'Base_viewHistoricalComparisonDiff?first_serial=%s&amp;second_serial=%s&amp;time=%s&amp;action=%s&amp;actor=%s'\
    % ( serial, next_serial, time, action, actor )
