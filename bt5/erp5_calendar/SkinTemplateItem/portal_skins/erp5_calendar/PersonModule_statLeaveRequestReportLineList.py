from Products.PythonScripts.standard import Object
request = container.REQUEST

return [Object( uid='new_0',
                total=request['total_time'],
                **request['total_time_per_resource']) ]
