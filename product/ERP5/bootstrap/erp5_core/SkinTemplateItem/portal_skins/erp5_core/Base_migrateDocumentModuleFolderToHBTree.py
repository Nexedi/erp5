portal = context.getPortalObject()

document_module = portal.document_module

document_module.migrateToHBTree(migration_generate_id_method="Base_generateIdFromCreationDate",
                                  new_generate_id_method="_generatePerDayId")

print "Document Module folder migrated to HBTree"
return printed
