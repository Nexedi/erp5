from six.moves import range
if not len(path_list):
  return
restrictedTraverse = context.getPortalObject().restrictedTraverse
if subscription_path:
  subscription = restrictedTraverse(subscription_path)
  getId = subscription.getGidFromObject
  getData = subscription.getDataFromDocument
else:
  getId = getData = None

method = context.z_catalog_syncml_document_list

def generateParameterList():
  parameter_append_list = []
  append = parameter_append_list.append
  parameter_dict = {}
  for property in method.arguments_src.split():
    parameter_dict[property] = parameter_value_list = []
    if property == 'getData':
      getter = getData
    elif property == 'getId':
      getter = getId
    else:
      getter = None
    if getter is None:
      getter = lambda obj, property=property: getattr(obj, property)()
    append((parameter_value_list, getter))
  return parameter_dict, parameter_append_list

MAX_PER_QUERY = 1000

for path in path_list:
  obj = restrictedTraverse(path)
  if obj.getPortalType() == "Integration Module":
    object_list = obj()
  else:
    object_list = [obj,]
  for x in range(0, len(object_list), MAX_PER_QUERY):
    parameter_dict, parameter_append_list = generateParameterList()
    for obj in object_list[x:x+MAX_PER_QUERY]:
      for value_list, getter in parameter_append_list:
        value_list.append(getter(obj))
    method(**parameter_dict)
