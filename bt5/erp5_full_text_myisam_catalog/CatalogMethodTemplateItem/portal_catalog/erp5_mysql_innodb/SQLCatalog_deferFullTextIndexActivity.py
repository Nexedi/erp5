from Products.ERP5Type.Utils import UpperCase
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized

method = context.z_catalog_fulltext_list
property_list = method.arguments_src.split()
parameter_dict = {}
failed_path_list = []
restrictedTraverse = context.getPortalObject().restrictedTraverse
for path in path_list:
  if not path: # should happen in tricky testERP5Catalog tests only
    continue
  obj = restrictedTraverse(path, None)
  if obj is None:
    continue
  try:
    tmp_dict = {}
    for property in property_list:
      getter = getattr(obj, property, None)
      if getter is not None and callable(getter):
        value = getter()
      else:
        value = getattr(obj, 'get%s' % UpperCase(property))()
      tmp_dict[property] = value
  except ConflictError:
    raise
  except Unauthorized: # should happen in tricky testERP5Catalog tests only
    continue
  except Exception as e:
    exception = e
    failed_path_list.append(path)
  else:
    for property, value in tmp_dict.items():
      parameter_dict.setdefault(property, []).append(value)

if len(failed_path_list):
  if len(parameter_dict):
    # reregister activity for failed objects only
    context.activate(activity='SQLQueue', priority=5).SQLCatalog_deferFullTextIndexActivity(path_list=failed_path_list)
  else:
    # if all objects are failed one, just raise an exception to avoid infinite loop.
    raise AttributeError('exception %r raised in indexing %r' % (exception, failed_path_list))

if parameter_dict:
  return method(**parameter_dict)
