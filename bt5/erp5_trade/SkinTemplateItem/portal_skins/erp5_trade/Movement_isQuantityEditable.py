"""This script is used to know if quantity can be edited by user.

* If this is not a movement (line containing lines or cell), user
cannot edit this line which is just a container, but no actual movement.

* If this line has variation category list, then it means it's a line that
will contain cell, so it's already not possible to set quantity, user have
to create cells and set quantities on cells.
"""

if not context.isMovement():
  return False

if context.getVariationCategoryList(omit_optional_variation=1) and not 'Cell' in context.getPortalType():
  return False

return True
