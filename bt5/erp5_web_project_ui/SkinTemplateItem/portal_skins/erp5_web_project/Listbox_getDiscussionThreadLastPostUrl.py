if url_dict:
  cell = brain.getObject()
  url_options = {
    'command': 'push_history',
    'options': {
      'jio_key': cell.getRelativeUrl(),
      'page': 'form',
      'view': 'view',
      'last_post': cell.DiscussionThread_getDiscussionPostCount()
    }
  }
  return url_options
