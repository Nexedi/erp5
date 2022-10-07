"""Returns a list of temp base objects"""
from Products.ERP5Type.Document import newTempBase
from six.moves import range
portal_object = context.getPortalObject()

limit = kw.get('limit')
list_start = int(kw.get('list_start', 0))
list_lines = int(kw.get('list_lines', 0))
size = list_lines or limit

result_list = []
result_list_append = result_list.append
for i in range(7):
  if list_start < i + 1<= list_start + size:
    caption = str(i)
    result_list_append(newTempBase(portal_object, caption, a='A' + caption, b='B' + caption))
  else:
    result_list_append(None)
return result_list
