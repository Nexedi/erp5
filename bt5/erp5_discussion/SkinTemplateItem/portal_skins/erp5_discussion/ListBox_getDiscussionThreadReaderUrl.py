thread = brain.getObject()
if url_dict:
  return {
    'command': 'push_history',
    'options': {
      'jio_key': thread.getRelativeUrl(),
      'page': 'form',
      'view': 'view_post_list'
    }
  }
return '%s/DiscussionThread_viewPostList' % thread.absolute_url()
