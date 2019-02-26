alpha = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
random_id = ''
for _ in range(0, 128):
  random_id += random.choice(alpha)

# Define Reference from ID provided by portal_ids
portal = context.getPortalObject()
type_definition = context.getTypeInfo()

short_portal_type = type_definition.getShortTitle()
if not short_portal_type:
  short_portal_type = ''.join(s for s in type_definition.getId() if s.isupper())

id_group = ('reference', short_portal_type)
default = 1
new_id = portal.portal_ids.generateNewId(id_group=id_group, default=default)
reference = '%s-%s%s' % (short_portal_type, new_id, random_id)

context.setReference(reference)
