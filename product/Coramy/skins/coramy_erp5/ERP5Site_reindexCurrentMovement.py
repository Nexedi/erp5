## Script (Python) "ERP5Site_reindexCurrentMovement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
folder_id_list = ['mouvement_mp', 'mouvement_pf', 'livraison_achat', 
                  'livraison_vente', 'livraison_fabrication']

for folder in context.portal_url.getPortalObject().objectValues(("ERP5 Folder",)):
  if folder.getId() in folder_id_list:
    print "#### Indexing contents inside folder %s ####" % folder.id
    for o in folder.objectValues():
      o.activate(priority=5).recursiveImmediateReindexObject()

return printed
