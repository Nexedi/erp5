portal = context.getPortalObject()

document_module = portal.document_module

error_list = []

try:
  document_module.migrateToHBTree(migration_generate_id_method="Base_generateIdFromCreationDate",
                                  new_generate_id_method="_generatePerDayId")
except Exception, e:
  error_list.append("Error in post upgrade script while migrating Document Module folder to HBTree: %s" % Exception(e))

return error_list
