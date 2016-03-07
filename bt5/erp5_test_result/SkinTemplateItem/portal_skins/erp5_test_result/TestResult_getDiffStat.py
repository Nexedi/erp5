value_list = context.getPortalObject().portal_selections \
               .getSelectionCheckedValueList(context.REQUEST.selection_name)
if not value_list:
  raise ValueError('No Test Result selected')

if len(value_list) != 2:
  raise ValueError('Two Test Results should be selected')

a, b = value_list

if a.getSimulationState() != "stopped" or b.getSimulationState() != "stopped":
  # it's useless to compare two results that are not yet completed
  return []

compared_prop_list = ('all_tests', 'errors', 'failures', 'skips')


d = {}
for prop in compared_prop_list:
  d[prop] = b.getProperty(prop) - a.getProperty(prop)

from Products.PythonScripts.standard import Object

return [Object(uid="new_", **d) ]
