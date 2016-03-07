portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

item_list = [('', '')]

for skin_selection in portal.portal_skins.getSkinSelections():
  item_list.append((Base_translateString("%s Style" % skin_selection), skin_selection))

return item_list
