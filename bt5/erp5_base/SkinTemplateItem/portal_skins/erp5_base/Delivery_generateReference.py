if context.getReference():
  return

object_type = context.getPortalType().replace(' ', '_')
parent_type = context.getParentValue().getPortalType().replace(' ', '_')
prefix = ''.join([x for x in object_type if x.isupper()])

id_group = '-'.join((parent_type, object_type))

new_id = context.generateNewId(id_group=id_group, default=1)

reference = "%s-%s" % (context.Base_translateString(prefix), new_id)

context.setReference(reference)
