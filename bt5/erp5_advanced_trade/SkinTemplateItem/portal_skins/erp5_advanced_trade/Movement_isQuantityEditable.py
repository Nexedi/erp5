"""This script is used to know if quantity can be edited by user.

* If this is not a movement (line containing lines or cell), user
cannot edit this line which is just a container, but no actual movement.

* If items are used, quantity is set by the item quantity.
"""

if not context.isMovement():
  return False

return not (context.getResource() and context.getResourceValue().getAggregatedPortalTypeList())
