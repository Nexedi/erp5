from Products.PythonScripts.standard import Object
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized
from Products.ERP5Type.Document import newTempBase
import six
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

def get_value_as_text(value):
  """check if values are unicode convertible (binary are not)
  """
  if not isinstance(value, six.text_type):
    try:
      if isinstance(value, bytes):
        value.decode('utf-8')
      else:
        str(value)
    except UnicodeDecodeError:
      value = binary_data_explanation
  return value


for prop_dict in sorted(context.getPropertyMap(), key=lambda prop: prop['id']):
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
    new_value = get_value_as_text(new_value)
    old_value = get_value_as_text(old_value)
    current_value = get_value_as_text(current_value)
    x = {'property_name': prop,
         'new_value': new_value,
         'old_value': old_value,
         'current_value': current_value,
    }
    tmp_obj = newTempBase(context,
                          '',
                          **x)
    tmp_obj.setProperty('serial', serial)
    tmp_obj.setProperty('next_serial', next_serial)
    tmp_obj.setProperty('action', action)
    tmp_obj.setProperty('actor', actor)
    tmp_obj.setProperty('time', time)
    result.append(tmp_obj)
return result
