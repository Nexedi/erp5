portal = context.getPortalObject()

# Get the list of all TempBase object for the selected properties which we
# will use to create a new object from the patch
selected_property_list = portal.portal_selections.getSelectionCheckedValueList(selection_name='diff_selection')

# Get the selected objects on which we applied the diff
selected_object_list = portal.portal_selections.getSelectionCheckedValueList(selection_name='web_page_module_view_web_page_list_selection')

raise AttributeError(selected_object_list)

# Get the old file on which we apply the patch
old_value = selected_object_list[0]
new_value = selected_object_list[0]

portal_diff = portal.portal_diff
new_object = portal_diff.patchPortalObject(old_value, selected_property_list)

return new_object
