if portal_type is None:
  portal_type = []

# return context.getMovementList(portal_type=portal_type)
# here we suppose we have only two level of portal type
#context.log("Delivery_getMovementList", "portal_type = %s" %(portal_type,))
#context.log("Delivery_getMovementList", "len portal_type = %s" % (len(portal_type),))

if same_type(portal_type, ""):
  return context.getMovementList(portal_type=portal_type)
if len(portal_type) != 2:
  # use catalog
  return context.getMovementList(portal_type=portal_type)

line_list = context.objectValues(portal_type=portal_type[0])

invert = 0
if len(line_list) == 0:
  # try with the second portal type
  line_list = context.objectValues(portal_type=portal_type[1])
  invert = 1
if len(line_list) == 0:
  return []
if len(portal_type) == 1:
  return line_list
cell_list = []
for line in line_list:
  if invert:
    cell_type = portal_type[0]
  else:
    cell_type = portal_type[1]
  cell_list.extend(list(line.objectValues(portal_type=cell_type)))

cell_list = context.Base_sortCurrencyCashList(cell_list)

return cell_list
