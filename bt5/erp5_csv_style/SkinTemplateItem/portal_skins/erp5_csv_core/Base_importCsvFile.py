from six.moves import range
def cleanString(str):
  clean_item = str
  if clean_item.find('"') != -1:
    clean_item = clean_item[1:-1].replace('""', '"')
  else:
    if clean_item != '':
      if clean_item.find('.') != -1:
        clean_item = float(clean_item)
      else:
        clean_item = int(clean_item)
    else:
      clean_item = None
  return clean_item

def splitCsvLine(str_line):
  unclean_list = []
  pieces_of_line = str_line.split(',')

  p_stack = ''
  for p in pieces_of_line:
    if p_stack == '':
      p_stack = p
    else:
      p_stack += ',%s' % p
    if p_stack.count('"') % 2 == 0:
      unclean_list.append(p_stack)
      p_stack = ''

  return [cleanString(x) for x in unclean_list]

request  = context.REQUEST
# Read first line (attribute's ids)
first_line = import_file.readline()
first_line = first_line.replace('\n', '')
csv_property_list = splitCsvLine(first_line)
# Read second line (attribute's titles)
second_line = import_file.readline()

# Read data lines
method = context.activate

i = 0
for line in iter(import_file.readline, ""):
  # XXX Currently, if the file is too big, there is too many
  # activities created in only one transaction
  # We need to reduce the number of activities
  # Ex: create 1 activity which manages 100 lines, by created itself 100
  # others activities
  i += 1
  line = line.replace('\n', '')
  csv_data_list = splitCsvLine(line)

  attribute_value_dict = dict([(csv_property_list[x], csv_data_list[x]) \
                               for x in range(len(csv_property_list))])

  method(priority=4, activity="SQLQueue").Base_importCsvLine(attribute_value_dict)
redirect_url = '%s?%s' % ( context.absolute_url()+'/'+'view', 'portal_status_message=Importing+CSV+file.')
request[ 'RESPONSE' ].redirect( redirect_url )
