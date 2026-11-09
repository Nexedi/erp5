from Products.PythonScripts.standard import html_quote
html = context.asStrippedHTML() or html_quote(context.getTitle())
for image in context.contentValues(portal_type='Image'):
  html += '<p><img src="%s" alt="%s"></p>' % (
    html_quote(image.File_getDownloadUrl()), html_quote(image.getTitle()))
return html
