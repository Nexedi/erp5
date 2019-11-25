"""
  Get all listbox fields that uses the same selection name.
"""

skins_tool = context.portal_skins
selection_name_dict = {}

ok_to_share_selection_form_list = ['Resource_viewInventory', 'Resource_viewMovementHistory']

for skin_name, skin_path_list in skins_tool.getSkinPaths():
  skins_tool.changeSkin(skin_name)
  for skin_folder in skin_path_list.split(','):
    for field_path, field in skins_tool.ZopeFind(
             skins_tool[skin_folder], obj_metatypes=['ProxyField', 'ListBox'], search_sub=1):
      form = field.aq_parent
      # in some rare cases sharing a selection can be done intentional so avoid them
      if form.getId() in ok_to_share_selection_form_list:
        continue
      # if the form looks like a field library, we don't care, because it is not used directly.
      if form.getId().endswith('FieldLibrary'):
        continue
      if field.meta_type == 'ProxyField':
        try:
          if field.get_recursive_tales('selection_name') != '':
            continue
          selection_name = field.get_recursive_orig_value('selection_name')
        except KeyError:
          continue
      elif field.meta_type == 'ListBox':
        if field.get_tales('selection_name')!='':
          continue
        selection_name = field.get_orig_value('selection_name')
      if selection_name == '':
        continue
      field_path_map = selection_name_dict.setdefault(selection_name, {})
      field_path_map.setdefault(field_path, set()).add(skin_folder)

# leave only duplicating ones
duplicating_selection_name_dict = {}
for selection_name, field_list in selection_name_dict.items():
  if len(field_list) > 1:
    duplicating_selection_name_dict[selection_name] = field_list

return duplicating_selection_name_dict
