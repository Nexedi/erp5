"""Utility script listing all relation fields that are using relation_setter_id feature.
This helps migrating them after r33837
"""
multi_relation_field_meta_type_list = ['RelationStringField',
                                       'MultiRelationStringField']
for field_path, field in context.ZopeFind(
            context.portal_skins, obj_metatypes=multi_relation_field_meta_type_list +
                                                ['ProxyField'], search_sub=1):
  if field.meta_type == 'ProxyField':
    template_field = field.getRecursiveTemplateField()
    if template_field is None or template_field.meta_type not in multi_relation_field_meta_type_list:
      continue

  relation_setter_id = field.get_value('relation_setter_id')
  if relation_setter_id:
    print(field_path, relation_setter_id)

return printed
