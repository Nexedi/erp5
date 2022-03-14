"""Initialise int_index and reference of object
It will set reference to int_index, as string.
In case if container is same type is its children, or context is cell,
reference is generated as <container_reference>.<children_index>:
  1
  1.1
  1.2
  1.2.1
  1.2.2
  1.3
  1.3.1
"""

from builtins import str
parent = context.getParentValue()
portal_type = context.getPortalType()

index = len(parent.contentValues(filter={"portal_type": portal_type}))

if parent.getPortalType() == portal_type or portal_type.endswith('Cell'):
  reference = "%s.%s" % (parent.getReference(), index)
else:
  reference = str(index)

context.edit(
  int_index = index,
  reference = reference
)
