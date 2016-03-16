def recursiveDocumentList(obj):
  ret = []
  ret.append(obj.getPath())
  for i in obj.objectValues():
    ret.extend(recursiveDocumentList(i))
  return ret

def splitCsvLine(str_line):
  unclean_list = []
  pieces_of_line = str_line.split(',')

  p_stack = ''
  for p in pieces_of_line:
    p_stack += p
    if p_stack.count('"')%2 == 0:
      unclean_list.append(p_stack)
      p_stack = ''

  clean_list = []
  for item in unclean_list:
    clean_item = item
    if clean_item.find('"') != -1:
      if len(clean_item) <= 2:
        clean_item = ''
      else:
        clean_item = clean_item[1:]
        clean_item = clean_item[:-1]
        clean_item = clean_item.replace('""', '"')
    else:
      if len(clean_item) > 0:      
        if clean_item.find('.') != -1:
          clean_item = float(clean_item)
        else:
          clean_item = int(clean_item)
      else:
        clean_item = None
    clean_list.append(clean_item)

  return clean_list

def getSubCategory(parent, id):
  try:
    return parent[id]
  except KeyError:
    return parent.newContent(id=id)

request  = context.REQUEST
csv_file_line_list = import_file.readlines()
csv_line_list = []

for csv_line in csv_file_line_list:
  csv_line_list.append( string.replace(csv_line, '\n', '').decode(encoding).encode('utf-8') )

object_list = []

csv_property_list = splitCsvLine(csv_line_list[0])
csv_title_list = splitCsvLine(csv_line_list[1])

for csv_line in csv_line_list[2:]:
  object = {}
  csv_data_list = splitCsvLine(csv_line)
  data_n = 0

  for property in csv_property_list:
    object[property] = csv_data_list[data_n]
    data_n += 1

  object_list.append(object)

root = context.getPortalObject().portal_categories
for path in gap_root_path.split('/'):
  root = getSubCategory(root, path)

existing_path_list = recursiveDocumentList(root)
existing_path_list.remove(root.getPath())

for object in object_list:
  description = object.get('Description', None) or ''
  gap = object.get('Gap', None) or ''
  title = object.get('Title', None) or ''
  gap = str(gap)
  if gap:
    gap = gap.replace('CLASSE ', '')
    print '+ %s - %s - %s' % (gap or '', title or '', description or '')
    path = root
    b = ''
    for a in gap:
      b = b + a
      path = getSubCategory(path, b)
    path.edit(reference=gap, title=title, description=description)
    try:
      existing_path_list.remove(path.getPath())
    except ValueError:
      pass

existing_path_list.sort(key=len, reverse=True)
for path in existing_path_list:
  object = context.restrictedTraverse(path)
  description = object.getDescription() or ''
  gap = object.getId() or ''
  title = object.getTitle() or ''
  print '- %s - %s - %s' % (gap or '', title or '', description or '')
  object.getParentValue().deleteContent(object.getId())

return printed
