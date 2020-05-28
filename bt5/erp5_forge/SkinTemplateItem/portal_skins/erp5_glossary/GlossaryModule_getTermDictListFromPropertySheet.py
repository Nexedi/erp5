ignore = ('custom',)
all_field_list = []
def iterate(obj):
  for i in obj.objectValues():
    if i.getId() in ignore:
      continue
    if i.meta_type=='ERP5 Form':
      all_field_list.extend(i.objectValues())
    elif i.isPrincipiaFolderish:
      iterate(i)

iterate(context.portal_skins)

properties = []
for i in property_sheet_list:
  properties.extend([x[0] for x in context.GlossaryModule_getPropertySheetAttributeList(i)])

dic = {}
for i in all_field_list:
  id_ = i.getId()
  title = i.get_value('title') or ''
  skin_id = i.aq_parent.aq_parent.getId()
  prefix = 'erp5_'
  if skin_id.startswith(prefix):
    skin_id = skin_id[len(prefix):]
  if id_.startswith('my_'):
    for p in properties:
      if id_=='my_%s' % p:
        key = (p, skin_id, title)
        dic[key] = i
  if id_.startswith('your_'):
    for p in properties:
      if id_=='your_%s' % p:
        key = (p, skin_id, title)
        dic[key] = i

result = []
for (reference, business_field, title) in dic.keys():
  language = 'en'
  field = dic[(reference, business_field, title)]
  description = field.get_value('description')
  field_path = '%s/%s/%s' % (field.aq_parent.aq_parent.getId(),
                            field.aq_parent.getId(),
                            field.getId())
  result.append({'reference':reference,
                 'language':language,
                 'business_field':business_field,
                 'title':title,
                 'description':description,
                 'field_path':field_path
                 })

return result
