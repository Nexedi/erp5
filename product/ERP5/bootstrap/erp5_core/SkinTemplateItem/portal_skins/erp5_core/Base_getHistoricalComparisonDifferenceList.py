"""
This script returns the list of TempBase object for displaying
the diff for different History Diff Views.

:params:
property_set: Name of the types of property we want to display
              in the list of Tempbase objects
serial:       Serial of the old object
next_serial:  Serial of the new object

The tempbase objects have following attributes which are being
used in the view:

path:   Name of the property
t1:     Old Value
t2:     New value
diff:   Unified Diff between t1 and t2
current_value: Current ZODB value of the property for the context
"""

from Products.ERP5Type.Document import newTempBase
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized
Base_translateString = context.Base_translateString

# Dictionary to bind the property set and the type of properties
# which are in the property set.
PROPERTY_TYPE_LIST = {
  'large_value_type' : ('text', 'data','content',),
  'single_line_type' : ('int', 'string', 'long', 'boolean', 'date', 'float',
                        'long', 'object', 'tales',),
  'iterator_type'    : ('tokens', 'selection', 'multiple_selection', 'lines',)
}

portal =  context.getPortalObject()
portal_diff = portal.portal_diff
try:
  context.HistoricalRevisions[serial]
except (ConflictError, Unauthorized):
  raise
except Exception:
  return [newTempBase(portal, Base_translateString('Historical revisions are'
                      ' not available, maybe the database has been packed'))]

if next_serial == '0.0.0.0':
  # In case the next serial is 0.0.0.0, we should always be considering the
  # new object as the current context
  new_getProperty = context.getProperty
  new = context
else:
  new = context.HistoricalRevisions[next_serial]
  new_getProperty = new.getProperty
old = context.HistoricalRevisions[serial]
result = []

# Use DiffTool to get beautified Diff between the properties of the objects.
# Thanks to Property Manager, we can use the propertyItems function
# to get the iterable for property ids and values and then convert
# them to dictionary.
diff = portal_diff.diffPortalObject(
                                    dict(old.propertyItems()),
                                    dict(new.propertyItems())
                                    ).asBeautifiedJSONDiff()

tempbase_list = []
uid = 900

for x in diff:
  property_type = context.getPropertyType(x['path'])
  # Check if the property type is in the list of property-types
  # for the property_set sent via parameter
  if property_type in PROPERTY_TYPE_LIST.get(property_set, ()):
    temp_obj = newTempBase(context,
                          x['path'],
                          **x)
    temp_obj.setProperty(
      'current_value',
      context.getProperty(x['path'])
    )
    temp_obj.setUid('new_%s' % uid)
    uid = uid + 1
    tempbase_list.append(temp_obj)

return tempbase_list
