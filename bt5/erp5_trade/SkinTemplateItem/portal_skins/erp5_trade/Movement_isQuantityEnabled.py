"""
This script is used to know if quantity should be shown to the user. Usually, not showing quantity happens when a total quantity is shown instead, meaning the line uses cells.

* If this is not a movement (line containing lines or cell), user cannot see quantity for this line which is just a container, but no actual movement.

* If this line has required variation category list, then it means it's a line that will contain cell, so total quantity will be used instead.

* If this line has optional variation category list, and already contain cells, total quantity should also be used.
"""

if not context.isMovement():
  return False

if not 'Cell' in context.getPortalType() and \
    (context.getVariationCategoryList(omit_optional_variation=1) or \
    context.hasCellContent(base_id='movement')):
  return False

return True
