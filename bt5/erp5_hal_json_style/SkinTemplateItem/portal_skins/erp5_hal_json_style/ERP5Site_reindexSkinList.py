portal = context.getPortalObject()
skin_tool = portal.portal_skins
for skin_folder in portal.portal_skins.objectValues():
  for skin_document in skin_folder.objectValues():
    if skin_document.meta_type == "ERP5 Form":
      # skin_document.setUid(None)
      skin_document.reindexObject()

print "skins ok"

return printed
