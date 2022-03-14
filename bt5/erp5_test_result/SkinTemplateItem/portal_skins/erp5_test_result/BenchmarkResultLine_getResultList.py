from builtins import zip
from Products.PythonScripts.standard import Object

cell_list = []
for name, result in zip(context.getProperty('result_header_list'), context.getProperty('result_list')):
  cell_list.append(Object(name=name, result=result))

return cell_list
