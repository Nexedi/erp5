category_list = context.portal_catalog(path="%portal_categories/gap2/br%")

for cat in category_list:
  id = cat.getId()
  newid = id.replace('_', '.')
  try:
    cat.getObject().setId(newid)
  except:
    pass
  print(newid)

print('Categories Renamed')
return printed
