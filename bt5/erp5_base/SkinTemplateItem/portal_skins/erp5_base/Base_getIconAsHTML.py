"""Create html to display icon of object)"""
icon = context.getIcon()
is_document = getattr(context, "isDocument", False) and context.getPortalType() != "Web Page"

html = "<img src='%s' alt='Object Icon' />" % icon

if (is_document):
  download_url = "%s/Base_download" % context.absolute_url()
  html = "<a href='%s' title='Download Document'>%s</a>" % (download_url, html)

return html
