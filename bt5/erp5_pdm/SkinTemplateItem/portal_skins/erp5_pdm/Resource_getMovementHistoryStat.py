from Products.PythonScripts.standard import Object

return [Object(uid="new_",
               total_quantity=context.getMovementHistoryStat(**kw)['total_quantity'],) ]
