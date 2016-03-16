skin_id_list = [x.getId() for x in context.portal_skins.objectValues('Folder')]
skin_id_list.sort()
return skin_id_list
