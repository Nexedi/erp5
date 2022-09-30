""" Retrieve the category list of the resource. """

result_list = []

# add to the list the shared variations
mapping_dict = {}
for mapping in context.contentValues(portal_type="Mapped Property Type"):
  prop = mapping.mapped_property
  for cell in mapping.getCellValueList(base_id=prop):
    cat_list = cell.getCategoryList()
    lcat_list = []
    for cat in cat_list:
      base = cat.split('/', 1)[0]
      try:
        cat = context.portal_categories.restrictedTraverse(cat).getTitle()
      except KeyError:
        base, path = cat.split('/', 1)
        iv = context.restrictedTraverse(path)
        cat = iv.getTitle()
      lcat_list.append(base+"/"+cat)
    getter_id = "get%s" %(prop.capitalize())
    getter = getattr(cell, getter_id)
    value = getter()
    mapping_dict[str(lcat_list)] = {'category' : lcat_list,}
    mapping_dict[str(lcat_list)][prop] = value

ordered_key_list = mapping_dict.keys()
ordered_key_list.sort()

return [mapping_dict[key] for key in ordered_key_list]
