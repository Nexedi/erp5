## Script (Python) "ERP5Site_reindexAll"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
print "#### Indexing categories ####"
for o in list(context.portal_categories.objectValues()):
  o.activate(passive_commit=1).recursiveImmediateReindexObject()

# We index simulation first to make sure we can calculate tests (ie. related quantity)
print "#### Indexing simulation ####"
for o in list(context.portal_simulation.objectValues()):
  o.activate(passive_commit=1).immediateReindexObject()

# We index templates secondly
print "#### Indexing templates ####"
for o in list(context.portal_templates.objectValues()):
  o.activate(passive_commit=1).immediateReindexObject()

# Then we index everything except inventories
for folder in context.portal_url.getPortalObject().objectValues(("ERP5 Folder",)):
  print "#### Indexing contents inside folder %s ####" % folder.id
  if folder.getId() not in ('inventaire_mp','inventaire_pf'):
    for o in list(folder.objectValues()):
      try:
        o.activate(passive_commit=1).recursiveImmediateReindexObject()
      except:
        #raise RuntimeError, o.getRelativeUrl()
        raise RuntimeError, 'error: folder=%s, o=%s'  % (repr(folder.getId()), repr(o))

# Then we index inventories
for folder in context.portal_url.getPortalObject().objectValues(("ERP5 Folder",)):
  print "#### Indexing contents inside folder %s ####" % folder.id
  if folder.getId() in ('inventaire_mp','inventaire_pf'):
    for o in list(folder.objectValues()):
      o.activate(passive_commit=1).recursiveImmediateReindexObject()

return printed
