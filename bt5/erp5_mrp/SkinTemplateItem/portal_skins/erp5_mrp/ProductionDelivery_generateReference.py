from builtins import range
if context.getReference():
  return

object_type = context.getPortalType().replace(' ', '_')
parent_type = context.getParentValue().getPortalType().replace(' ', '_')
uppercase_list = ['%c' % x for x in range(ord('A'), ord('Z') + 1)]
prefix = ''.join([x for x in object_type if x in uppercase_list])

# dirty hack
# Production Order upper case letters are same as Purchase Order upper case letters
# So I (Luke) replaced first letter with R - pRoduction, that way we have
# RO for Production Order, RPL for Production Packing List, RR for Manufacturing Execution
prefix = 'R' + prefix[1:]

id_group = '-'.join((parent_type, object_type))

new_id = context.generateNewId(id_group=id_group, default=1)

reference = "%s %s" % (context.Base_translateString(prefix), new_id)

context.setReference(reference)
