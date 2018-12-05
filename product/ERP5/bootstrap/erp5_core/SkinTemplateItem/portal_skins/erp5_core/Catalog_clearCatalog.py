# Script to clear Catalog

REQUEST = context.REQUEST
form = REQUEST.form
clear_catalog = form.get('clear_catalog')

if not clear_catalog:
  return REQUEST.RESPONSE.redirect(context.absolute_url() +
                            '/view?portal_status_message=Catalog%20Not%20Cleared')

return context.manage_catalogClear(REQUEST)
