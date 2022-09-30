portal_skins = context.getPortalObject().portal_skins
skin_folder = portal_skins.manage_addProduct['OFSP'].manage_addFolder(skin_folder_id)

# Add the new skin folder at the top of portal_skins.
for skin_name, selection in portal_skins.getSkinPaths():
  new_selection = ('%s,' % skin_folder_id + selection).replace(",,",",")
  portal_skins.manage_skinLayers(skinpath = (new_selection,) ,
                                 skinname = skin_name,
                                 add_skin = 1)

return getattr(portal_skins, skin_folder_id)
