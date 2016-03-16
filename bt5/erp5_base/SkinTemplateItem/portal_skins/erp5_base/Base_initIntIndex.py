"""Initialise int_index of object
"""

parent = context.getParentValue()
portal_type = context.getPortalType()

index = len(parent.contentValues(filter={"portal_type": portal_type}))

context.edit(int_index=index)
