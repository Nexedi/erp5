from Products.ERP5Type.Document import newTempBase

portal =  context.getPortalObject()
portal_diff = portal.portal_diff

# Get the selcted values for the web page selection
selected_obj_list = portal.portal_selections.getSelectionCheckedValueList(selection_name=list_selection_name)

# Return the 1st object path from the selected_obj_list
return selected_obj_list[0].getPath()
