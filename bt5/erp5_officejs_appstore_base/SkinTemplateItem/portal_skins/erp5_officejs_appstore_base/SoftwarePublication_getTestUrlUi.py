url = context.SoftwarePublication_getTestUrl()
if url_dict:
  return {
    'command': 'raw',
    'options': {
      'url': url
    }
  }
return url
