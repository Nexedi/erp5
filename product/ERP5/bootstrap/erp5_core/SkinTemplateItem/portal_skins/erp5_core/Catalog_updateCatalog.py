# This script deals with updating(deleting then reindexing) of sql catalog
# XXX: Keep in mind that here we are talking about sql catalog.
# But after that process, it updates erp5 catalog with the objects and indexes
# of updated sql catalog.

REQUEST = context.REQUEST
form = REQUEST.form
update_catalog = form.get('update_catalog')

if not update_catalog:
  return REQUEST.RESPONSE.redirect(context.absolute_url() +
                    '/view?portal_status_message=Catalog%20Not%20Updated')

return context.manage_catalogReindex(REQUEST)
