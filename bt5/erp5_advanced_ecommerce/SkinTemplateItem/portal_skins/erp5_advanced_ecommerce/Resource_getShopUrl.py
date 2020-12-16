variation = context.REQUEST.get('default_displayed_variation', None)
relative_url = context.getRelativeUrl()
absolute_url = context.getAbsoluteUrl()
if not variation or not variation.startswith(relative_url):
  return '%s/%s' % (absolute_url, 'Resource_viewAsShop')

return '%s/%s?variation=%s' % (absolute_url, 'Resource_viewAsShop', variation)
