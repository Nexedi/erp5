"""
  Print all field that uses non existing scripts as external_validator
"""
portal = context.getPortalObject()
skins_tool = portal.portal_skins

for skin_name, skin_path_list in skins_tool.getSkinPaths():
  skins_tool.changeSkin(skin_name)
  for skin_folder in skin_path_list.split(','):
    for form_path, form in skins_tool.ZopeFind(
             skins_tool[skin_folder], obj_metatypes=['ERP5 Form', 'ERP5 Report'], search_sub=1):
      for field in form.get_fields():
        if field.meta_type == 'ProxyField':
          if field.get_recursive_tales('external_validator'):
            continue
          try:
            external_validator = field.get_recursive_orig_value('external_validator')
          except KeyError:
            continue
        else:
          if field.get_tales('external_validator'):
            continue
          try:
            external_validator = field.get_orig_value('external_validator')
          except KeyError:
            continue
        if external_validator:
          method_name = external_validator.getMethodName()
          if portal.restrictedTraverse(method_name, None) is None:
            print "{form_path}/{field_id} uses an external validator non existant in {skin_name}: {method_name}".format(
                form_path=form_path,
                field_id=field.getId(),
                skin_name=skin_name,
                method_name=method_name,
            )

return printed
