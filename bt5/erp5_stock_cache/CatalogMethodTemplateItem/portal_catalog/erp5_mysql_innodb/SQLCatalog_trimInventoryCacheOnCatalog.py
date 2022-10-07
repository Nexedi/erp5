from Products.ERP5Type.Errors import ProgrammingError
from six.moves import range

zTrimInventoryCacheFromDateOnCatalog = getattr(context, 'SimulationTool_zTrimInventoryCacheFromDateOnCatalog', None)
if zTrimInventoryCacheFromDateOnCatalog is None:
  return

min_date = None
for loop_item in range(len(uid)):
    if not isInventoryMovement[loop_item] and isMovement[loop_item] and getResourceUid[loop_item]:
        if getDestinationUid[loop_item] and getStopDate[loop_item]:
            if min_date:
                min_date = min(min_date, getStopDate[loop_item])
            else:
                min_date = getStopDate[loop_item]
        if getSourceUid[loop_item] and getStartDate[loop_item]:
            if min_date:
                min_date = min(min_date, getStartDate[loop_item])
            else:
                min_date = getStartDate[loop_item]

try:
    zTrimInventoryCacheFromDateOnCatalog(uid_list=uid, min_date=min_date)
except ProgrammingError:
    # Create table if it does not exits
    # Then no need to flush an empty table
    context.SimulationTool_zCreateInventoryCache()
