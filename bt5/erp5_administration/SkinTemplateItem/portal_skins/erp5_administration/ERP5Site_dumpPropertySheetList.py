if ignore_property_sheet_list is None:
  ignore_property_sheet_list = []

for ps in sorted(context.getPortalObject().portal_property_sheets.contentValues(), key=lambda x:x.getId()):
  for pd in sorted(ps.contentValues(), key=lambda x:x.getId()):
    ps_id = ps.getId()
    if ps_id in ignore_property_sheet_list:
      continue
    print(ps.getId())
    info_list = ['id', 'portal_type', 'reference']
    std_prop_list = ['elementary_type', 'property_default', 'storage_id', 'multivaluated', 'range', 'preference', 'read_permission', 'write_permission', 'translatable', 'translation_domain']
    if pd.getPortalType() == 'Standard Property':
      info_list += std_prop_list
    elif pd.getPortalType() == 'Acquired Property':
      info_list += std_prop_list + [ 'acquisition_portal_type', 'content_acquired_property_id_list', 'acquisition_accessor_id', 'acquisition_copy_value', 'alt_accessor_id_list', 'content_portal_type', 'content_translation_acquired_property_id_list', 'acquisition_object_id_list', 'acquisition_mask_value', 'acquisition_base_category_list',]
    elif pd.getPortalType() == 'Category Property':
      info_list += []
    elif pd.getPortalType() == 'TALES Constraint':
      info_list += ['expression'] + [p for p in pd.propertyIds() if p.startswith('message')]
    elif pd.getPortalType() in ('Category Existence Constraint', 'Category Existence Constraint'):
      info_list += ['constraint_base_category_list'] + [p for p in pd.propertyIds() if p.startswith('message')]
    elif pd.getPortalType() in ('Category Membership State Constraint', 'Acquired Category Membership State Constraint'):
      info_list += ['membership_portal_type_list', 'constraint_base_category_list', 'workflow_state_list', 'workflow_variable'] + [p for p in pd.propertyIds() if p.startswith('message')]

    elif pd.getPortalType() in ('Property Existence Constraint', ):
      info_list += ['constraint_property_list'] + [p for p in pd.propertyIds() if p.startswith('message')]
    elif pd.getPortalType() in ('Content Existence Constraint', ):
      info_list += ['constraint_portal_type'] + [p for p in pd.propertyIds() if p.startswith('message')]
    elif pd.getPortalType().endswith('Constraint'):
      info_list += [] + [p for p in pd.propertyIds() if p.startswith('message')]
    else:
      print("(not supported)",pd.getRelativeUrl(), pd.getPortalType())


    print(" ", "\n  ".join(['%s: %s' % (prop, pd.getProperty(prop)) for prop in sorted(info_list)]))
    print()

return printed
