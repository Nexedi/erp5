"""
This scripts calls the crawlContent API and returns a nice message
to the user. If no URL is defined, warns the user.
"""
translateString = context.Base_translateString
if not context.asURL():
  portal_status_message = translateString("Please specify a URL before trying to start to crawl content.")
else:
  portal_status_message = translateString("Started crawling external source.")
  context.crawlContent()
return context.Base_redirect('view', keep_items = dict(portal_status_message=portal_status_message), **kw)
