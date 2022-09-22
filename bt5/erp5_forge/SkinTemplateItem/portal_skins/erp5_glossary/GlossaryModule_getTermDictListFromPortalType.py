skip_id_list = [
  'uid', 'rid', 'sid', 'categories',
]
remove_suffix_list = [
  '_id', '_relative_url', '_title',
]

# First, create portal_type => business_field dict based on
# Business Template definitions.
bt_list = [x for x in \
           context.getPortalObject().portal_templates.contentValues() \
           if x.getInstallationState() in ('installed', 'not_installed')]
bt_list.sort(key=lambda x:int(x.getRevision() or 0))
bt_dict = dict([(x.getTitle(), [y for y in x.getTemplatePortalTypeIdList()] + \
                               [y.split('|')[1].strip() for y in x.getTemplatePortalTypePropertySheetList()] \
                 ) for x in bt_list])
business_field_dict = {}
prefix = 'erp5_'
for bt_title, bt_portal_type_list in bt_dict.items():
  if bt_title.startswith(prefix):
    bt_title = bt_title[len(prefix):]
  for portal_type in bt_portal_type_list:
    business_field_dict[portal_type] = bt_title

# Then, create a glossary for each property.
result = []
language = 'en'
for portal_type in portal_type_list:
  business_field = business_field_dict.get(portal_type, portal_type)
  id_dict = {}
  property_sheet_list = \
      context.GlossaryModule_getPropertySheetList(portal_type)
  for property_sheet in property_sheet_list:
    for property_id, property_desc in \
        context.GlossaryModule_getPropertySheetAttributeList(property_sheet):
      for x in remove_suffix_list:
        if property_id.endswith(x):
          property_id = property_id[:-len(x)]
      if property_id in id_dict or property_id in skip_id_list:
        continue
      result.append({'reference':property_id,
                     'language':language,
                     'business_field':business_field,
                     'title':' ',
                     'description':property_desc,
                     'field_path':'%s/%s' % (portal_type, property_sheet)
                     })
      id_dict[property_id] = True

#result.sort(key=lambda x:(x['business_field'], x['reference']))
return result
