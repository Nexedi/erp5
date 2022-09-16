from Products.ERP5Type.Utils import UpperCase
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized
import six

method = context.z_catalog_fulltext_list
property_list = method.arguments_src.split()
parameter_dict = {x: [] for x in property_list}
for group_object in object_list:
  tmp_dict = {}
  try:
    obj = group_object.object
    for property in property_list:
      getter = getattr(obj, property, None)
      if callable(getter):
        value = getter()
      else:
        value = getattr(obj, 'get%s' % UpperCase(property))()
      tmp_dict[property] = value
  except ConflictError:
    raise
  except Unauthorized: # should happen in tricky testERP5Catalog tests only
    # Fake activity success: if indexation cannot View document, ignore it.
    group_object.result = None
  except Exception:
    group_object.raised()
  else:
    for property, value in six.iteritems(tmp_dict):
      parameter_dict[property].append(value)
    group_object.result = None

if parameter_dict:
  return method(**parameter_dict)
