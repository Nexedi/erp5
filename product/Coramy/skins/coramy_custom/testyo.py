## Script (Python) "testyo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
movement_list = context.getMovementList()
movement_group = context.collectMovement(movement_list)

invoice_line_list = context.buildInvoiceLineList(movement_group)
return repr(invoice_line_list)

dict = context.showDict()
item_list = dict.items()
item_list.sort()
s = ''
for key,val in item_list:
  s += "%s: %s\n" % (str(key), str(val))
return s

ret = []

invoice_line_list = context.contentValues(filter={'portal_type':'Invoice Line'})
for invoice_line in invoice_line_list:
  cell_range = invoice_line.getCellRange(base_id='movement')
  ret.append(cell_range)

return repr(ret)
