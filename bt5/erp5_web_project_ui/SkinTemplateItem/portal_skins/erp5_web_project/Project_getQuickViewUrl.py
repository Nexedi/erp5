from Products.ERP5Type.Log import log
request = context.REQUEST

if url_dict:
  jio_key = context.getRelativeUrl()
  return {
    'command': 'display',
    'options': {
      'jio_key': jio_key,
      'editable': False
    },
    'view_kw': {
      'view': 'Project_viewQuickOverview',
      'jio_key': jio_key,
    }
  }

elif url_dict:
  return {}
