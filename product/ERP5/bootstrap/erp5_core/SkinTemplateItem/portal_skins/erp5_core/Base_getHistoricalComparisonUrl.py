"""
This URL script is used for Historical comparison list.
There are two cases handled here. If it is the first
row of the list(having serial as 0.0.0.0), then we don't
want to have any URL as there is no comparison needed,
thus we return empty dictionary in case of renderJS UI and
nothing for XHTMl UI.
"""

request = context.REQUEST

serial = getattr(brain, 'serial', '0.0.0.0')
next_serial = getattr(brain, 'next_serial', '0.0.0.0')

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
                'time': brain.time,
                'action': brain.action,
                'actor': brain.actor,
              }
            }
           }
  return 'Base_viewHistoricalComparison?serial=%s&amp;next_serial=%s&amp;time=%s&amp;action=%s&amp;actor=%s'\
      % ( serial, next_serial, brain.time, brain.action, brain.actor )

elif url_dict:
  return {}
