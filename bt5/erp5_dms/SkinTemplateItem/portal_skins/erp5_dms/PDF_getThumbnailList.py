"""
  THis script returns a suitable slide list of PDF thumbnails
  for current form selection.
  It's to be used in a listbox.
"""
from Products.ERP5Type.Document import newTempBase

content_information = context.getContentInformation()
page_number = int(content_information.get('Pages', 0))
limit = kw.get('limit', (0, 0))
list_start = int(kw.get('list_start', 0))
list_lines = int(kw.get('list_lines', 0))
size = list_lines or limit[1]

list_end = list_start + size
page_list = range(page_number)

result = []
for i in page_list[list_start:list_end]:
  x = {'title': '%s' %i, 
       'frame':'%s' %i} # frame is used by listbox render field
  temp_object = newTempBase(context, x['title'], **x)
  result.append(temp_object)
return result
