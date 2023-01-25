request = context.REQUEST

display_cache = {}
def display(x):
  if x not in display_cache:
    display_cache[x] = "%s" % getERP5CategoryUrl(x)
  return display_cache[x]

def sort(x,y):
  return cmp(display(x), display(y))

def getERP5CategoryUrl(category):
  if category.getPortalType() == "Base Category":
    return category.getTitle()
  else:
    return "%s/%s" % (getERP5CategoryUrl(category.getParentValue()), category.getTitle())

def isUrlInTupleList(tuple_list, url):
  for (k,v) in tuple_list:
    if v == url:
      return True
  return False

if context.getPortalType() == "Integration Category Mapping":
  try:
    uid = "_".join(context.getParentValue().getRelativeUrl().split("/")[2:])
    category_url = request.form["field_listbox_destination_reference_new_%s" % uid]
  except:
    category_url = context.getParentValue().getDestinationReference()
  if category_url is not None and category_url != "":
    container = context.restrictedTraverse("portal_categories/%s" % category_url)
  try:
    uid = "_".join(context.getParentValue().getRelativeUrl().split("/")[2:])
    new_destination_reference = request.form["field_listbox_destination_reference_new_%s" % uid]
    if new_destination_reference == "":
      value = request.form["field_listbox_destination_reference_new_%s" % context.getId()]
      return [(value,value)]
    else:
      value = request.form["field_listbox_destination_reference_new_%s" % context.getId()]
      container = context.restrictedTraverse("portal_categories/%s" % new_destination_reference)
      category_child_list = container.getCategoryChildItemList(base=1, checked_permission='View', display_method=display, sort_method=sort)
      if isUrlInTupleList(category_child_list, value):
        return  category_child_list
      else:
        return [(value, value)] + category_child_list[1:]
  except:
    pass
  if container is None or category_url is None:
    return [('','')]
else:
  container = context.portal_categories
if container ==  context.portal_categories:
  return [('', '')] + [(bc.getTranslatedTitle(),
             bc.getId()) for bc in container.contentValues(sort_on=(('translated_title', 'asc'),))]
else:
  return container.getCategoryChildItemList(base=1, checked_permission='View', display_method=display, sort_method=sort)
