from builtins import filter
from builtins import str
from Products.ERP5Type.Document import newTempBase
portal = context.getPortalObject()
document_to_inspect = context.getAgentValue()
property_map_list = document_to_inspect.getPropertyMap()

def filterPropertyMapList(property_map):
  # Keep only some kind of properties
  # We assume that categories, dates, and numerical values
  # doesn't carry compromising data
  restricted_property_list = ('id', 'rid', 'id_group',
                              'id_generator', 'last_id',
                              'reference',)
  return property_map['type'] in ('string', 'data', 'text',) and \
    property_map['id'] not in restricted_property_list and \
    document_to_inspect.getProperty(property_map['id']) and \
    document_to_inspect.hasProperty(property_map['id'])

property_map_list = list(filter(filterPropertyMapList, property_map_list))
property_map_list = document_to_inspect.Base_updatePropertyMapListWithFieldLabel(property_map_list)

MAX_LENGHT = 25
listbox_object_list = []
for index, property_map in enumerate(property_map_list):
  temp_object = newTempBase(portal, 'temp%s' % (index,))
  try:
    property_value = str(document_to_inspect.getProperty(property_map['id']), 'utf-8')[:MAX_LENGHT]
  except UnicodeDecodeError:
    property_value = 'Not viewable: binary content'

  temp_object.edit(uid=property_map['id'],
                   property_id=property_map['id'],
                   property_label=portal.Base_translateString(property_map.get('label', '')),
                   property_description=portal.Base_translateString(property_map.get('description', '')),
                   property_value=property_value)
  listbox_object_list.append(temp_object)

return listbox_object_list
