"""
This URL script returns the URL for current value for the
properties in the Historical Comparison Diff.
"""
from Products.ERP5Type.Log import log
if brain is None:
  brain = context

# Get the name of property from the brain and send it as
# parameter to the next view
path = brain.getProperty('path')
property_name = path.split('/')[2]
log(context.aq_parent)
log(brain)
if url_dict:
  return {'command': 'push_history',
          'options': {
            'jio_key': context.getRelativeUrl(),
            },
          'view_kw': {
            'jio_key': context.getRelativeUrl(),
            'view': 'Base_viewCurrentValueForLargeText'
          }
    }

return 'Base_viewCurrentValueForLargeText?property_name=%s' % property_name
