from Products.ERP5Type.Errors import ProgrammingError

zTrimInventoryCacheFromDateOnUncatalog = getattr(context, 'SimulationTool_zTrimInventoryCacheFromDateOnUncatalog', None)
if zTrimInventoryCacheFromDateOnUncatalog is None:
  return

try:
    zTrimInventoryCacheFromDateOnUncatalog(uid=uid)
except ProgrammingError:
    # Create table if it does not exits
    # Then no need to flush an empty table
    context.SimulationTool_zCreateInventoryCache()
