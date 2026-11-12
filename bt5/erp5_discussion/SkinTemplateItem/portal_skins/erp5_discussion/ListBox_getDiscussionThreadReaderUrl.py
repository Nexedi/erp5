thread = brain.getObject()
if url_dict:
  jio_key = thread.getRelativeUrl()
  return {
    'command': 'push_history',
    'options': {
      'jio_key': jio_key
    },
    'view_kw': {
      'view': 'view_post_list',
      'jio_key': jio_key
    }
  }
return '%s/DiscussionThread_viewPostList' % thread.absolute_url()
