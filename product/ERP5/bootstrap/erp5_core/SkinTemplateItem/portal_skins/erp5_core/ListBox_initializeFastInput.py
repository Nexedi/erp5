from Products.ERP5Type.Document import newTempBase
if listbox_id is None:
  listbox_id = 'listbox'

request = context.REQUEST

# It must be possible to initialise the fast input, and to add empty lines after
if 'my_empty_line_number' in request:
  empty_line_number = request['my_empty_line_number']


l = []
first_empty_line_id = 1
portal_object = context.getPortalObject()
int_len = 3

if hasattr(request, listbox_id):
  listbox_key = "%s_key" % listbox_id
  # initialize the listbox
  listbox=request[listbox_id]

  keys_list = sorted(listbox, key=int)

  if keys_list != []:
    first_empty_line_id = int(keys_list[-1])+1

  for i in keys_list:
    o = newTempBase(portal_object, i)
    o.setUid('new_%s' % str(i).zfill(int_len))

    is_empty = 1

    for key in listbox[i]:
      value = listbox[i][key]
      # 0 was added because of checkbox field in some fast input
      if (value not in ['',None,0]) and (key != listbox_key):
        is_empty = 0
      if ('field_errors' in request):
        is_empty = 0
      #o.edit(key=listbox[i][key])
      o.setProperty(key,listbox[i][key])

    if not is_empty:
      l.append(o)

# add empty lines
if not('field_errors' in request):
  for i in range(first_empty_line_id,first_empty_line_id+empty_line_number):

    o = newTempBase(portal_object, str(i))
    o.setUid('new_%s' % str(i).zfill(int_len))
    # zfill is used here to garantee sort order - XXX - cleaner approach required
    l.append(o)


return l
