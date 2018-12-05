# Script to clear Reserved UIDs from Catalog

REQUEST = context.REQUEST
form = REQUEST.form
clear_reserved = form.get('clear_reserved')

if not clear_reserved:
  return REQUEST.RESPONSE.redirect(context.absolute_url() +
              '/view?portal_status_message=Reserved%20UIDs%20Not%20Cleared')

return context.manage_catalogClearReserved(REQUEST)
