from Products.ERP5Type.Document import newTempBase

num = 0
listbox_lines = []

request = context.REQUEST

# Get spreadsheet data
try:
  spreadsheets = request['ooo_import_spreadsheet_data']
except KeyError:
  return []

for spreadsheet in spreadsheets.keys():
  # In the case of empty spreadsheet do nothing
  if spreadsheets[spreadsheet] not in (None, []):
    column_name_list = spreadsheets[spreadsheet][0]

    for column in column_name_list:
      safe_id = context.Base_getSafeIdFromString('%s%s' % (spreadsheet, column))
      num += 1
      # int_len is used to fill the uid of the created object like 0000001
      int_len = 7
      o = newTempBase(context, safe_id)
      o.setUid('new_%s' % str(num).zfill(int_len)) # XXX There is a security issue here
      o.edit(uid='new_%s' % str(num).zfill(int_len)) # XXX There is a security issue here
      o.edit(
          id=safe_id,
          spreadsheet_name=spreadsheet,
          spreadsheet_column=column
      )
      listbox_lines.append(o)

return listbox_lines
