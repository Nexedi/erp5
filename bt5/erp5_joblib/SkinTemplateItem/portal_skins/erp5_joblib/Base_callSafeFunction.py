if REQUEST is not None: 
  raise Unauthorized

from Products.ERP5Type.Log import log

log("Executing batch_function on %s" % context.getRelativeUrl())

result = batch_function()

log("Result of batch_function on %s: %s" % (context.getRelativeUrl(), result))

return result
