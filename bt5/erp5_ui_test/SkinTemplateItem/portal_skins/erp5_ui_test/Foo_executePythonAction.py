if not foo_url:
  return context.Base_redirect('view', keep_items={'portal_status_message': 'Missing expected foo_url parameter', 'portal_status_level': 'error'})
else:
  return context.Base_redirect('view', keep_items={'portal_status_message': 'foo_url parameter equals %s' % foo_url})
