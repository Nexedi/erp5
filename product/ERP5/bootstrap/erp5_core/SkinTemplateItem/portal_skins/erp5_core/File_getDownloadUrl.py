if brain is None:
  brain = context
url = '%s/Base_download' % brain.absolute_url()

if url_dict:
  return {'command': 'raw',
          'options': {
            'url': url
            }
    }
return url
