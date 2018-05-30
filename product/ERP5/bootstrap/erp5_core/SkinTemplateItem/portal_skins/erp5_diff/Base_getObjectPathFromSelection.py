portal =  context.getPortalObject()

# There would be multiple cases where this script will be called, but the only
# case where we use selections to get the diff. Hence, we check for the condition
# that list_selection_name is not None.
if list_selection_name is not None:
  # Get the selcted values for the web page selection
  selected_obj_list = portal.portal_selections.getSelectionCheckedValueList(selection_name=list_selection_name)

  # Return the 1st object path from the selected_obj_list
  return selected_obj_list[selection_index].getRelativeUrl()
