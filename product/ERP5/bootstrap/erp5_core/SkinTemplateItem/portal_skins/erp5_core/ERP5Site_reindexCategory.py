error_list = []
return_list = []

for category in context.portal_categories.objectValues():
  #print "#### Indexing inside the folder %s ####" % 'portal_categories'
  error_list += context.reindexAll(object=category,request=context)

nb_types = {}

for error in error_list:
  # We count the number of each portal type
  if error[1]=='portal_type':
    portal_type = error[3]
    if nb_types.has_key(portal_type):
      nb_types[portal_type] = nb_types[portal_type] + 1
    else:
      nb_types[portal_type] = 1
  else: 
    #print error
    return_list.append(error)

for portal_type in nb_types.keys():
  # Find the number of each portal type in the catalog
  count_result = context.portal_catalog.countResults(portal_type=portal_type)
  nb_catalog = count_result[0][0]
  if nb_types[portal_type] != nb_catalog:
    message = "XXX Warning for %s: there is %i lines in the catalog instead of %i" % \
      (portal_type, nb_catalog, nb_types[portal_type])
    return_list.append(('Count Error', 'PortalRoot_reindexAll',1,message))
  #else: print "%s: %i" % (portal_type,nb_types[portal_type])

return return_list
