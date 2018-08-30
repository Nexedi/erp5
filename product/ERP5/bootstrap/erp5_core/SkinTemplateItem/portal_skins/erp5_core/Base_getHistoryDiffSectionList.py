# This script is used to return the list of Report Sections
# we will use for displaying diffs.

from Products.ERP5Form.Report import ReportSection

path = context.getPhysicalPath()
request = context.REQUEST

# There are 2 sections we expect to be used:
# One with Diff Viewer and another with old, new and
# current values.
return [
  ReportSection(
    form_id="Base_viewHistoricalComparisonDiffList",
    level=1,
    listbox_display_mode="FlatListMode",
    path=path,
    selection_params = {
      'serial': request.get('serial', None),
      'next_serial': request.get('next_serial', None),
    },
    temporary_selection=False),
  ReportSection(
    form_id="Base_viewHistoricalComparisonValueList",
    level=1,
    listbox_display_mode="FlatListMode",
    path=path,
    selection_params = {
      'serial': request.get('serial', None),
      'next_serial': request.get('next_serial', None),
    },
    temporary_selection=False),
]
