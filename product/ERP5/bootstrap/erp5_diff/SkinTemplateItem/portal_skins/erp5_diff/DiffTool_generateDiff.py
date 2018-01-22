from Products.ERP5Type.Document import newTempBase

portal =  context.getPortalObject()
portal_diff  = portal.portal_diff

# Get the list selection name as we will need it to get the selected object for
# the current list which we need to diff between
list_selection_name = kw.get('list_selection_name', '')

# Get the selcted values for the web page selection
selected_obj_list = portal.portal_selections.getSelectionCheckedValueList(selection_name=list_selection_name)

# Using portal_diff, find out the Beautified Diff between the selected values
diff = portal_diff.diffPortalObject(selected_obj_list[0], selected_obj_list[1]).asBeautifiedJSONDiff()

# Return a list of TempBase objects which can be displayed in a listbox
tempbase_list = []
uid = 999
for x in diff:
  temp_obj = newTempBase(portal,
                        x['path'],
                        **x)
  temp_obj.setUid(int(uid))
  uid = uid + 1
  tempbase_list.append(temp_obj)

return tempbase_list
