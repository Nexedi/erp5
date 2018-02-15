from Products.ERP5Type.Document import newTempBase

portal =  context.getPortalObject()
portal_diff = portal.portal_diff

# Get the list selection name as we will need it to get the selected object for
# the current list which we need to diff between
#list_selection_name = kw.get('list_selection_name', '')

# Get the selcted values for the web page selection
selected_obj_list = portal.portal_selections.getSelectionCheckedValueList(selection_name=list_selection_name)

# Return the 1st object path from the selected_obj_list
return selected_obj_list[1].getPath()
