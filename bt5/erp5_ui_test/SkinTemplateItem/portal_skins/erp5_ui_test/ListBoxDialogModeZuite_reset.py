"""Reset everything for the test."""

# Clean up the contents.
for name in ('foo_module', 'bar_module'):
  module = getattr(context, name)
  module.manage_delObjects(list(module.objectIds()))
  module.setLastId(1)

# Reset the foo module listbox
form = context.Foo_viewSelectBarDialog

default_columns = '\n'.join(( 'id | ID'
                            , 'title | Title'
                            , 'quantity | Quantity'
                            ))
form.listbox.ListBox_setPropertyList(
    field_title            = 'Bars'
  , field_columns          = default_columns
  , field_sort             = 'id'
  , field_editable_columns = default_columns
  , field_list_method      = 'portal_catalog'
  , field_count_method     = ''
  , field_selection_name   = 'foo_bar_selection'
  , field_portal_types     = 'Bar'
  , field_search           = 'checked'
  , field_select           = 'checked'
  , field_list_action      = 'Folder_viewContentList'
  , field_editable         = ''
  )


# Reset the selection.
def resetSelection(selection_name):
  selection_tool = context.portal_selections
  if selection_tool.getSelectionFor(selection_name) is not None:
    selection_tool.setSelectionToAll(selection_name, reset_domain_tree=True, reset_report_tree=True)
    selection_tool.setSelectionSortOrder(selection_name, [])
    selection_tool.setSelectionColumns(selection_name, [])
    selection_tool.setSelectionStats(selection_name, [])
    selection_tool.setListboxDisplayMode(context.REQUEST, 'FlatListMode', selection_name)
    selection_tool.setSelectionParamsFor(selection_name, {})

resetSelection('foo_selection')
resetSelection('foo_line_selection')
resetSelection('bar_selection')
resetSelection('foo_bar_selection')


pref = getattr(context.portal_preferences, "erp5_ui_test_preference", None)
if pref is None:
  pref = context.portal_preferences.newContent(id="erp5_ui_test_preference", portal_type="Preference")
pref.setPreferredListboxListModeLineCount(10)
if pref.getPreferenceState() == 'disabled':
  pref.enable()

return 'Reset Successfully.'
