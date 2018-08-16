"""
This script is used to return the list of Report Sections
used for displaying diffs. Also, we use this script
to calculate the diff and then send them to the report
sections to be displayed according to their types.

We expect atmost 3 types of Report Sections:
- For large text content types (where `current_value` would
  be displayed via links)
- For single line types (with old, new and current values)
- For iterable types (with Diff Viewer gadget and current_value)
"""

from Products.ERP5Form.Report import ReportSection
from Products.ERP5Type.Document import newTempBase
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized
Base_translateString = context.Base_translateString

path = context.getPhysicalPath()
request = context.REQUEST
portal =  context.getPortalObject()
portal_diff = portal.portal_diff
serial = request.get('serial', None)
next_serial = request.get('next_serial', None)

try:
  context.HistoricalRevisions[serial]
except (ConflictError, Unauthorized):
  raise
except Exception:
  return [newTempBase(portal, Base_translateString('Historical revisions are'
                      ' not available, maybe the database has been packed'))]

if next_serial == '0.0.0.0':
  # In case the next serial is 0.0.0.0, we should always be
  # considering the new object as the current context
  new_getProperty = context.getProperty
  new = context
else:
  new = context.HistoricalRevisions[next_serial]
  new_getProperty = new.getProperty
old = context.HistoricalRevisions[serial]
result = []

diff = portal_diff.diffPortalObject(
                                    dict(old.propertyItems()),
                                    dict(new.propertyItems())
                                    ).asBeautifiedJSONDiff()

diff_dict = {}

for d_ in diff:
  # Add current value to the `diff`
  d_['current'] = context.getProperty(d_['path'])
  property_type = context.getPropertyType(d_['path'])

  # Separate the diff according to the property types
  if property_type in ('data', 'text', 'content'):
    if 'large_value_type' not in diff_dict:
      diff_dict['large_value_type'] = [d_,]
    else:
      diff_dict['large_value_type'].append(d_)

  elif property_type in ('int', 'string', 'long', 'boolean', 'date','float',
                         'long', 'object', 'tales'):
    if 'single_line_type' not in diff_dict:
      diff_dict['single_line_type'] = [d_,]
    else:
      diff_dict['single_line_type'].append(d_)

  elif property_type in ('tokens', 'selection', 'multiple_selection', 'lines'):
    if 'iterator_type' not in diff_dict:
      diff_dict['iterator_type'] = [d_,]
    else:
      diff_dict['iterator_type'].append(d_)

# We now create sections for the different property types
report_section_list = []
for key, val in diff_dict.iteritems():

  if key == 'large_value_type':
    report_section_list.append(
      ReportSection(
        form_id="Base_viewHistoricalComparisonDiffLinkList",
        level=1,
        listbox_display_mode="FlatListMode",
        path=path,
        selection_params = {
          'property_set': 'large_value_type',
          'serial': request.get('serial', None),
          'next_serial': request.get('next_serial', None),
        },
        temporary_selection=False))

  elif key == 'single_line_type':
    report_section_list.append(
      ReportSection(
        form_id="Base_viewHistoricalComparisonValueList",
        level=1,
        listbox_display_mode="FlatListMode",
        path=path,
        selection_params = {
          'property_set': 'single_line_type',
          'serial': request.get('serial', None),
          'next_serial': request.get('next_serial', None),
        },
        temporary_selection=False))

  elif key == 'iterator_type':
    report_section_list.append(
      ReportSection(
        form_id="Base_viewHistoricalComparisonDiffList",
        level=1,
        listbox_display_mode="FlatListMode",
        path=path,
        selection_params = {
          'property_set': 'iterator_type',
          'serial': request.get('serial', None),
          'next_serial': request.get('next_serial', None),
        },
        temporary_selection=False))

return report_section_list
