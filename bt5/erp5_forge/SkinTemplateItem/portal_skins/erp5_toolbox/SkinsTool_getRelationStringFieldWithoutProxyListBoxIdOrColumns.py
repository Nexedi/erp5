multi_relation_field_meta_type_list = ['RelationStringField',
                                       'MultiRelationStringField']
for field_path, field in context.ZopeFind(
            context.portal_skins, obj_metatypes=multi_relation_field_meta_type_list +
                                                ['ProxyField'], search_sub=1):
  if field.meta_type == 'ProxyField':
    template_field = field.getRecursiveTemplateField()
    if template_field is None or template_field.meta_type not in multi_relation_field_meta_type_list:
      continue

  # acceptable if in a field library ?
  form = field.aq_parent
  if form.getId().endswith('FieldLibrary'):
    continue

  if not (field.get_value('proxy_listbox_ids') or field.get_value('columns')):
    print(field_path)
    continue

  for path, name in field.get_value('proxy_listbox_ids'):
    if context.restrictedTraverse(path, None) is None:
      print('   PROBLEM: field %s uses an invalid form for %s: %s' % (field_path, name, path))
    else:
      proxy_listbox = context.restrictedTraverse(path)
      if proxy_listbox.meta_type not in ('ProxyField', 'ListBox'):
        print('   PROBLEM: field %s uses an invalid proxy with %s meta_type' % (field_path, proxy_listbox.meta_type))
return printed
