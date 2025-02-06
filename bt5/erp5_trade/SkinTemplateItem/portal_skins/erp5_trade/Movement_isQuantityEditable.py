"""
This script is used to know if quantity can be edited by user.

* If quantity is not enabled on the movement, quantity cannot be set.

* If items are required, quantity is set by the item quantity.
"""

if !context.Movement_isQuantityEnabled():
  return False

return not (context.getResource() and context.getResourceValue().getRequiredAggregatedPortalTypeList())
