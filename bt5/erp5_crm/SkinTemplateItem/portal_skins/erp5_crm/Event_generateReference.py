"""Owner Proxy Role allows anonymous users to create events
through web sites. cf. Event_init
"""
portal = context.getPortalObject()
type_definition = context.getTypeInfo()

short_portal_type = type_definition.getShortTitle()
if not short_portal_type:
  short_portal_type = ''.join(s for s in type_definition.getId() if s.isupper())

new_id = portal.portal_ids.generateNewId(id_group=repr(('reference', short_portal_type)), default=1)
reference = '%s-%s' % (short_portal_type, new_id)

context.setReference(reference)
