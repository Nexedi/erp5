if not hasattr(context, 'asURL'):
  if url_dict:
    # new JS interface needs dict
    return {}
  return None

if url_dict:
  return {
    'command': 'raw',
    'options': {
      'url': context.asURL()
    }
  }
return context.asURL()
