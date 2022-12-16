from Products.ERP5Type.Message import translateString

portal = context.getPortalObject()

if skin_folder_name not in portal.portal_skins.objectIds():
  portal.portal_skins.manage_addFolder(skin_folder_name)
if skin_folder_name not in (context.getTemplateSkinIdList() or []):
  context.setTemplateSkinIdList(
    sorted(tuple(context.getTemplateSkinIdList() or []) + (skin_folder_name, )))

skin_folder = portal.portal_skins[skin_folder_name]

if skin_layer_priority:
  marker = []
  if skin_folder.getProperty("business_template_skin_layer_priority", marker) is marker:
    skin_folder.manage_addProperty("business_template_skin_layer_priority", skin_layer_priority, "float")
  else:
    skin_folder.manage_changeProperties({"business_template_skin_layer_priority": skin_layer_priority})

if skin_layer_list:
  all_skin_layers_selected = len(skin_layer_list) == len(portal.portal_skins.getSkinPaths())
  for skin_name, selection in portal.portal_skins.getSkinPaths():
    if skin_name in skin_layer_list:
      selection = selection.split(',')
      if skin_folder_name not in selection:
        portal.portal_skins.manage_skinLayers(
          skinpath=[skin_folder_name,] + list(selection),
          skinname=skin_name,
          add_skin=1,)
      if not all_skin_layers_selected:
        registered_skin = '%s | %s' % (skin_folder_name, skin_name)
        registered_skin_selection_list = context.getTemplateRegisteredSkinSelectionList() or []
        if registered_skin not in registered_skin_selection_list:
          context.setTemplateRegisteredSkinSelectionList(
            sorted(tuple(registered_skin_selection_list) + (registered_skin, )))

  if not all_skin_layers_selected:
    marker = []
    if skin_folder.getProperty("business_template_registered_skin_selections", marker) is marker:
      skin_folder.manage_addProperty("business_template_registered_skin_selections", " ".join(skin_layer_list), "tokens")
    else:
      skin_folder.manage_changeProperties({"business_template_registered_skin_selections": skin_layer_list})

return context.Base_redirect(form_id,
                             keep_items={'portal_status_message': translateString("Skin folder created.")})
