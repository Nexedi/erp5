import csv

def recursiveDocumentList(obj):
  ret = []
  ret.append(obj.getPath())
  for i in obj.objectValues():
    ret.extend(recursiveDocumentList(i))
  return ret

def getSubCategory(parent, category_id):
  try:
    return parent[category_id]
  except KeyError:
    return parent.newContent(id=category_id)


root = context.getPortalObject().portal_categories
for path in gap_root_path.split('/'):
  root = getSubCategory(root, path)

existing_path_list = recursiveDocumentList(root)
existing_path_list.remove(root.getPath())

for property_dict in list(csv.DictReader(import_file)):
  description = property_dict.get('Description', None) or ''
  gap = property_dict.get('Gap', None) or ''
  title = property_dict.get('Title', None) or ''
  gap = str(gap)
  if gap:
    gap = gap.replace('CLASSE ', '')
    print('+ %s - %s - %s' % (gap or '', title or '', description or ''))
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
  document = context.restrictedTraverse(path)
  description = document.getDescription() or ''
  gap = document.getId() or ''
  title = document.getTitle() or ''
  print('- %s - %s - %s' % (gap or '', title or '', description or ''))
  document.getParentValue().deleteContent(document.getId())

return printed
