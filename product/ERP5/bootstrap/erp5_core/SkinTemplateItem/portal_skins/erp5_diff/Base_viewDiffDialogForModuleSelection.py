"""
This script redirects to Diff Tool Dialog. It is used for the case where we
select 2 objects from a Module and try to get the diff between them.

In case there is selection of more or less than 2 objects, it simply redirects
back to the module with a portal message.
"""
request = context.REQUEST
portal = context.getPortalObject()

list_selection_name = request.get('list_selection_name', None)
# In case the list_selection_name is there, it can be the case of selection
# from the module
if list_selection_name is not None:
  selected_obj_list = portal.portal_selections.getSelectionCheckedValueList(selection_name=list_selection_name)
  # Check if the number of selected object is 2 only. otherwise redirect back to
  # context with a portal message.
  if len(selected_obj_list) != 2:
    message = context.Base_translateString("This action can only compare exactly 2 objects.")
    return context.Base_redirect('view', keep_items={'portal_status_message': message})
  else:
    # Keep the `list_selection_name` in keep_items as we will be needing it
    # while displaying the paths of the selected objects.
    return context.Base_redirect('ERP5Site_viewDiffTwoObjectDialog',
                                  keep_items={
                                    'list_selection_name': list_selection_name,
                                    'your_first_path': selected_obj_list[0].getRelativeUrl(),
                                    'your_second_path': selected_obj_list[1].getRelativeUrl()
                                             })
