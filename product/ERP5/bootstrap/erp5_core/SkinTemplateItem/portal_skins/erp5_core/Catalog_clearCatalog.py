# Script to clear Reserved UIDs from Catalog

form = context.REQUEST.form
clear_catalog = form.get('clear_catalog')

REQUEST = context.REQUEST

if not clear_catalog:
  url = context.absolute_url()+'/view'
  return REQUEST.RESPONSE.redirect(url)

return context.manage_catalogClear(REQUEST)
