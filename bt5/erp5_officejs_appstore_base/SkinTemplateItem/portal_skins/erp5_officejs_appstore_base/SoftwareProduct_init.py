# Define Reference from ID provided by portal_ids
portal = context.getPortalObject()
type_definition = context.getTypeInfo()

# XXX Hardcoded
short_portal_type = "OSP"

new_id = portal.portal_ids.generateNewId(id_group=repr(('reference', short_portal_type)), default=1)
reference = '%s-%s' % (short_portal_type, new_id)
context.setReference(reference)
