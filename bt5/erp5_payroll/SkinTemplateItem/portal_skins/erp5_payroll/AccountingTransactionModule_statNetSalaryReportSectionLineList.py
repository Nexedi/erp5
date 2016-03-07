from Products.PythonScripts.standard import Object
request = container.REQUEST
return [Object(total_price=request['total_price'])]
