##parameters=request=None

error_list = []
return_list = []

context.portal_catalog.catalog_object(context.portal_categories,None)

for category in context.portal_categories.objectValues():
  #print "#### Indexing inside the folder %s ####" % 'portal_categories'
  error_list += context.reindexAll(object=category,request=context)

for object in context.portal_simulation.objectValues():
  #print "#### Indexing inside the folder %s ####" % 'portal_simulation'
  error_list += context.reindexAll(object=object,request=context)

for folder in context.objectValues(("ERP5 Folder",)):
  #print "#### Indexing inside the folder %s ####" % folder.id
  error_list += folder.reindexAll(object=folder,request=context)

nb_types = {}

for error in error_list:
  # We count the number of each portal type
  if error[1]=='portal_type':
    type = error[3]
    if nb_types.has_key(type):
      nb_types[type] = nb_types[type] + 1
    else:
      nb_types[type] = 1
  else: 
    #print error
    return_list.append(error)

for type in nb_types.keys():
  # Find the number of each portal type in the catalog
  count_result = context.portal_catalog.countResults(portal_type=type)
  nb_catalog = count_result[0][0]
  if nb_types[type] != nb_catalog:
    message = "XXX Warning for %s: there is %i lines in the catalog instead of %i" % \
      (type,nb_catalog,nb_types[type])
    return_list.append(('Count Error', 'PortalRoot_reindexAll',1,message))
  #else: print "%s: %i" % (type,nb_types[type])

return return_list
