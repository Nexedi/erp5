portal = context.getPortalObject()
current_object = context.getObject()
rccm = current_object.getSourceReference()
org_list = []
org_result = portal.organisation_module.searchFolder(source_reference=rccm)
org_list = [org.getObject() for org in org_result if org.getObject() != context.getObject()]
return org_list
