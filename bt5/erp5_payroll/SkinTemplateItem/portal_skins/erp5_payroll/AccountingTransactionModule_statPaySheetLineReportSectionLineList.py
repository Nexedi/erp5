from Products.PythonScripts.standard import Object

request = context.REQUEST

return [Object(employee= request['employee_total'],
               employer=request['employer_total'],
               base=request['base_total'],
               total= request['total']
              )
       ]
