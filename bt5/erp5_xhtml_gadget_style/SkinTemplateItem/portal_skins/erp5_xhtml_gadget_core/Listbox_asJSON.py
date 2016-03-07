from json import dumps

REQUEST = context.REQUEST
form = getattr(context, form_id)
listbox = getattr(form, listbox_id)
lines = listbox.get_value("lines")
columns = listbox.get_value("columns")
listbox_renderer = context.getListBoxRenderer(listbox, REQUEST)

# listbox pagination for jqgrid
# XXX: jqgrid always sends page which makes server side slection be resetted
selection_name = listbox.get_value("selection_name")
page = REQUEST.get("page")
if page is not None:
  page = int(page)
  REQUEST.form['page_start'] = page
  context.portal_selections.setPage(list_selection_name=selection_name, \
                                    listbox_uid=[],
                                    REQUEST=REQUEST)
  #context.log ("Set page = %s %s" %(page, selection_name))

row_list= []
line_list = listbox_renderer.query()
for line in line_list:
  value_line = line.getValueList() 
  row = {"id":   value_line[0][0],
         "cell": [x[1] for x in value_line]}
  row_list.append(row)
  
# return real listbox data here by using form and context
listbox_max_lines = int(listbox_renderer.getMaxLineNumber())
total_pages = listbox_renderer.total_pages
total_line =  int(listbox_renderer.total_size)
current_page = int(listbox_renderer.current_page) + 1
current_page_max = listbox_max_lines * current_page
current_page_start = (listbox_max_lines * (current_page - 1)) + 1
current_page_stop  = (total_line < current_page_max) and total_line or current_page_max


#context.log("%s %s %s %s %s %s" %(listbox_max_lines, total_line, current_page,
#                                  current_page_max, current_page_start, current_page_stop))

json = {"page": page,
        "total": total_pages,
        "records": total_line,
        "rows":row_list}

return dumps(json)
