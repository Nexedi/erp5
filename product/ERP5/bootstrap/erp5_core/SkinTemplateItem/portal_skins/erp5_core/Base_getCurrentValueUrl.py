"""
This URL script returns the URL for current value for the
properties in the Historical Comparison Diff.
"""
if brain is None:
  brain = context

# Get the name of property from the brain and send it as
# parameter to the next view
path = brain.getProperty('path')
property_name = path.split('/')[-1]

if url_dict:
  parent = brain.aq_parent
  return {'command': 'push_history',
          'options': {
            'jio_key': parent.getRelativeUrl(),
            },
          'view_kw': {
            'jio_key': parent.getRelativeUrl(),
            'view': 'display_current_value',
            'extra_param_json': {
              'property_name': property_name
            }
          }
    }

return 'Base_viewCurrentValueForLargeText?property_name=%s' % property_name
