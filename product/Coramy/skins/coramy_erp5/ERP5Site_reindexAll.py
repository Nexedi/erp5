## Script (Python) "ERP5Site_reindexAll"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
error_list = []
return_list = []

context.portal_catalog.catalog_object(context.portal_categories,None)

base_url = '/'.join(context.getPhysicalPath())

print "#### Indexing categories ####"
for id in list(context.portal_categories.objectIds()):
  context.portal_activities.newMessage('SQLDict', '%s/portal_categories/%s' % (base_url, id), {}, 'recursiveImmediateReindexObject')

# We index simulation first to make sure we can calculate tests
print "#### Indexing simulation ####"
for id in list(context.portal_simulation.objectIds()):
  context.portal_activities.newMessage('SQLDict', '%s/portal_simulation/%s' % (base_url, id), {}, 'immediateReindexObject')

for folder in context.portal_url.getPortalObject().objectValues(("ERP5 Folder",)):
  print "#### Indexing contents inside folder %s ####" % folder.id
  for id in list(folder.objectIds()):
    context.portal_activities.newMessage('SQLDict', '%s/%s/%s' % (base_url, folder.getId(), id), {}, 'recursiveImmediateReindexObject')

return printed
