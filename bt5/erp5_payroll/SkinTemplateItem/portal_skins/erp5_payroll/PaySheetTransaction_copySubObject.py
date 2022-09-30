'''This script copies sub objects of models (corresponding to the
portal_type_list) in the paysheet.
'''

sub_object_list = context.getInheritedObjectValueList(
                         portal_type_list, property_list=property_list)

# Erase existing sub objects with same reference
delete_id_list = []
for sub_object in sub_object_list:
  sub_object_reference = sub_object.getProperty('reference', sub_object.getId())
  for existing_sub_object in context.contentValues(portal_type=portal_type_list):
    if sub_object_reference == existing_sub_object.getProperty(
                                    'reference', existing_sub_object.getId()):
      delete_id_list.append(existing_sub_object.getId())

if delete_id_list:
  context.manage_delObjects(ids=delete_id_list)

sub_object_by_model = {}
for sub_object in sub_object_list:
  sub_object_by_model.setdefault(
           sub_object.getParentValue(), []).append(sub_object.getId())

for model, sub_object_id_list in sub_object_by_model.items():
  copy_data = model.manage_copyObjects(sub_object_id_list)
  context.manage_pasteObjects(copy_data)
