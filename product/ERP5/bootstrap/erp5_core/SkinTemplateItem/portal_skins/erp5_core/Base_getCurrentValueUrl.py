"""
This URL script returns the URL for current value for the
properties in the Historical Comparison Diff.
"""
if brain is None:
  brain = context

# Get the name of property from the brain and send it as
# parameter to the next view
path = brain.getProperty('path')
property_name = path.split('/')[2]

if url_dict:
  return {'command': 'raw',
          'options': {
            'url': 'google.com'
            }
    }

return 'Base_viewCurrentValueForLargeText?property_name=%s' % property_name
