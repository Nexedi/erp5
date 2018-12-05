# Script to clear Catalog

REQUEST = context.REQUEST

if not clear_catalog:
  return REQUEST.RESPONSE.redirect(context.absolute_url() +
                            '/view?portal_status_message=Catalog%20Not%20Cleared')

return context.manage_catalogClear(REQUEST)
