for folder in context.objectValues(("ERP5 Folder",)):
  print "#### Exporting the folder %s ####" % folder.id
  folder.exportAll(dir='/var/lib/zope/')

print "#### Exporting the folder %s ####" % 'portal_catalog'
context.manage_exportObject(id='portal_catalog')

print "#### Exporting the folder %s ####" % 'portal_categories'
context.manage_exportObject(id='portal_categories')

print "#### Exporting the folder %s ####" % 'portal_types'
context.manage_exportObject(id='portal_types')

print "work done"
return printed

