from Products.PythonScripts.standard import Object
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized
Base_translateString = context.Base_translateString

try:
  context.HistoricalRevisions[serial]
except (ConflictError, Unauthorized):
  raise
except Exception: # POSKeyError
  return [Object(property_name=Base_translateString('Historical revisions are'
                      ' not available, maybe the database has been packed'))]

if next_serial == '0.0.0.0':
  new_getProperty = context.getProperty
else:
  new = context.HistoricalRevisions[next_serial]
  new_getProperty = new.getProperty
old = context.HistoricalRevisions[serial]
result = []

binary_data_explanation = Base_translateString("Binary data can't be displayed")
base_error_message = Base_translateString('(value retrieval failed)')

for prop_dict in context.getPropertyMap():
  prop = prop_dict['id']
  error = False
  try:
    current_value = context.getProperty(prop)
  except TypeError:
    error = True
    current_value = base_error_message
  try:
    old_value = old.getProperty(prop)
  except TypeError:
    error = True
    old_value = base_error_message
  try:
    new_value = new_getProperty(prop)
  except TypeError:
    error = True
    new_value = base_error_message
  if new_value != old_value or error:
    # check if values are unicode convertible (binary are not)
    if isinstance(new_value, (str, unicode)):
      try:
        unicode(str(new_value), 'utf-8')
      except UnicodeDecodeError:
        new_value = binary_data_explanation
    if isinstance(old_value, (str, unicode)):
      try:
        unicode(str(old_value), 'utf-8')
      except UnicodeDecodeError:
        old_value = binary_data_explanation
    if isinstance(current_value, (str, unicode)):
      try:
        unicode(str(current_value), 'utf-8')
      except UnicodeDecodeError:
        current_value = binary_data_explanation

    result.append( Object( property_name=prop,
                           new_value=new_value,
                           old_value=old_value,
                           current_value=current_value))
return result
