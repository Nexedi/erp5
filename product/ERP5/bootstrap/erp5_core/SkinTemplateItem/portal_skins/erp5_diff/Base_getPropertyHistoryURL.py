if brain is None:
  brain = context

# Get the name of property from the brain and send it as
# parameter to the next view
path = brain.getProperty('name')
property_name = path.split('/')[-1]

if url_dict:
  parent = brain.aq_parent
  jio_key = parent.getRelativeUrl()
  return {
    'command': 'push_history',
    'options': {
      'jio_key': jio_key,
    },
    'view_kw': {
      'jio_key': jio_key,
      'view': 'property_history_view',
      'extra_param_json': {
        'property_name': property_name,
      }
    }
  }

return 'Base_viewPropertyHistoryList?property_name=%s' % property_name
