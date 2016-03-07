from Products.ERP5Type.Document import newTempBase
from string import zfill
if listbox_id is None:
  listbox_id = 'listbox'

request = context.REQUEST

# It must be possible to initialise the fast input, and to add empty lines after
if request.has_key('my_empty_line_number'):
  empty_line_number = request['my_empty_line_number']


l = []
first_empty_line_id = 1
portal_object = context.getPortalObject()
int_len = 3

def get_fast_input_discriminant(line_id):
  line = listbox.get(line_id)
  if line is not None:
    resource_id = line.get('resource_id')
    if resource_id is not None:
      cash_currency = context.currency_cash_module.get(resource_id)
      if cash_currency is not None and cash_currency.hasBasePrice():
        return (cash_currency.getPortalType(), -cash_currency.getBasePrice(), line_id) # First sort by base price (desc), then by line id (asc)
  return line_id

def sort_container(x, y):
  x = listbox.get(x)
  y = listbox.get(y)
  result = cmp(x.get('date'), y.get('date'))
  if result == 0:
    result = cmp(x.get('reference'),y.get('reference'))
  return result

def sort_fast_input_lines(x, y):
  criterion_x = get_fast_input_discriminant(x)
  criterion_y = get_fast_input_discriminant(y)
  if criterion_x < criterion_y:
    return -1
  elif criterion_x > criterion_y:
    return 1
  else:
    return 0

if hasattr(request, listbox_id):
  listbox_key = "%s_key" % listbox_id
  # initialize the listbox 
  listbox=request[listbox_id]
  keys_list = listbox.keys()
  if keys_list != []:
    if context.getPortalType() in ('Monetary Issue',):
      keys_list.sort(sort_container)
    else:
      keys_list.sort(sort_fast_input_lines)
    first_empty_line_id = int(keys_list[-1])+1

  for i in keys_list:
    o = newTempBase(portal_object, i)
    o.setUid('new_%s' % zfill(i,int_len))

    is_empty = 1

    for key in listbox[i]:
      value = listbox[i][key]
      # 0 was added because of checkbox field in some fast input
      if (value not in ['',None,0]) and (key != listbox_key):
        is_empty = 0
      if (request.has_key('field_errors')):
        is_empty = 0
      #o.edit(key=listbox[i][key])
      o.setProperty(key,listbox[i][key])

    if not is_empty:
      l.append(o)
    
# add empty lines
if not(request.has_key('field_errors')):
  for i in range(first_empty_line_id,first_empty_line_id+empty_line_number):

    o = newTempBase(portal_object, str(i))
    o.setUid('new_%s' % zfill(i,int_len))   
    # zfill is used here to garantee sort order - XXX - cleaner approach required
    l.append(o)


return l
