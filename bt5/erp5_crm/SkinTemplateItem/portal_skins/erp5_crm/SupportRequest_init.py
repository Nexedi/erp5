# Define Reference from ID provided by portal_ids
portal = context.getPortalObject()
type_definition = context.getTypeInfo()

short_portal_type = type_definition.getShortTitle()
if not short_portal_type:
  short_portal_type = ''.join(s for s in type_definition.getId() if s.isupper())

id_group = ('reference', short_portal_type)
default = 1
new_id = portal.portal_ids.generateNewId(id_group=id_group, default=default)
reference = '%s-%06d' % (short_portal_type, new_id)

context.setReference(reference)
