# This script deals with updating(deleting then reindexing) of sql catalog
# XXX: Keep in mind that here we are talking about sql catalog.
# But after that process, it updates erp5 catalog with the objects and indexes
# of updated sql catalog.

REQUEST = context.REQUEST
return context.manage_catalogReindex(REQUEST)
