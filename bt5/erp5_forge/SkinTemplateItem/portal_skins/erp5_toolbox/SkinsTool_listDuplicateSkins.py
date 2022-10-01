"""List all skins that are present in more than one skin folder, ordered by
priority.
"""

# make sure context is the skins tool
stool = context.portal_skins

print('<html><body>')
skins_by_name = {}

for skin_key, skin_path_list in stool.getSkinPaths():
  if skin_key == stool.getDefaultSkin():
    skin_path_list = skin_path_list.split(',')
    for skin_path in skin_path_list:
      # skip CMF paths
      if skin_path in ('control', 'zpt_control',
                       'generic', 'zpt_generic',
                       'content', 'zpt_content'):
        continue
      skin_folder = stool.portal_skins[skin_path]
      for skin in skin_folder.objectValues():
        skins_by_name.setdefault(skin.getId(), []).append(skin_path)

for skin_name, location_list in skins_by_name.items():
  if len(location_list) > 1:
    print(skin_name, '<br/>')
    for location in location_list:
      print("&nbsp;" * 3, '<a href="%s/%s/%s/manage_main">%s</a><br/>' % (stool.absolute_url(), location, skin_name, location))

print('</body></html>')
return printed
