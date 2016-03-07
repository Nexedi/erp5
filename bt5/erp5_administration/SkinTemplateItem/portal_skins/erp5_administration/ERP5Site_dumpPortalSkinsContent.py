for skin_folder in context.getPortalObject().portal_skins.objectValues('Folder'):
  for skin in skin_folder.objectValues():
    print ";".join((skin_folder.getId(), skin.getId(), skin.meta_type))
    
return '\n'.join(sorted(printed.splitlines()))
