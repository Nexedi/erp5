if url_dict:
  jio_key = context.getRelativeUrl()
  return {
    'command': 'index',
    'options': {
      'jio_key': jio_key,
      'editable': True
    },
    'view_kw': {
      'view': 'Project_viewQuickOverview',
      'jio_key': jio_key,
    }
  }

else:
  return {}
