portal = context.getPortalObject()
portal_diff = portal.portal_diff

# Get the list of all TempBase object for the selected properties which we
# will use to create a new object from the patch
selection_name = 'diff_selection_' + context.getId()

# Get the checked UIDs of the selected objects for the given selection
selection = portal.portal_selections.getSelectionFor(selection_name)
checked_uid_list = selection.getCheckedUids()
# These checked UIDs then will be used to patch the properties of the old value

# Get the selected objects on which we applied the diff
selected_obj_list = portal.portal_selections.getSelectionCheckedValueList(selection_name='web_page_module_view_web_page_list_selection')

# Generate the diff for the 2 objects again here and then use the UID to get the
# properties we want to patch for old object

diff = portal_diff.diffPortalObject(selected_obj_list[0], selected_obj_list[1]).asBeautifiedJSONDiff()
applicable_diff_list = []

for i in checked_uid_list:
  try:
    applicable_diff_list.append(diff[i])
  except IndexError:
    pass

# Get the old file on which we apply the patch
old_value = selected_obj_list[0]

new_object = portal_diff.patchPortalObject(old_value, applicable_diff_list)

url = context.absolute_url() + new_object.getPath()
REQUEST = context.REQUEST
REQUEST.RESPONSE.redirect(url)
