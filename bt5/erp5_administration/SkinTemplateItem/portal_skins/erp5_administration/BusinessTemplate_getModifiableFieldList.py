from Products.ERP5Type.Document import newTempBase
portal = context.getPortalObject()
field_list = []

action_title_item_list = [
  ['0_keep_non_proxy_field', 'To be proxified'],
  ['0_keep_dead_proxy_field', 'Dead Proxy Field'],
  ['0_check_delegated_value', 'Check Delegated Values'],
  ['0_unused_proxy_field', 'Unused Proxy Field'],
  ['1_create_form', 'Create Form'],
  ['2_unproxify_field', 'Unproxify Field'],
  ['4_delete_form', 'Delete Old Field Library'],
  ]
action_title_dict = dict(action_title_item_list)

field_library_id_dict = {
  'erp5_pdm': 'Base_viewPDMFieldLibrary',
  'erp5_crm': 'Base_viewCRMFieldLibrary',
  'erp5_mrp': 'Base_viewMRPFieldLibrary',
}

modified_object_dict = {}

def calculateFieldLibraryID(id):
  # The field library name could be automatically calculated or hardcoded in
  # the script
  return field_library_id_dict.get(id) or 'Base_view%sFieldLibrary' % \
      ''.join([x.capitalize() for x in id.split('_')[1:]])

def getForm(skin_folder, form_id):
  try:
    return skin_folder[form_id]
  except KeyError:
    return None

bt_title = context.getTitle()
field_library_id = calculateFieldLibraryID(bt_title)

field_library_dict = {}
# Check if the Field Library exists
skin_id_list = context.getTemplateSkinIdList()
if skin_id_list:
  if bt_title in skin_id_list:
    main_skin_id = bt_title
  elif skin_id_list:
    main_skin_id = skin_id_list[0]
  form_path = '%s/%s' % (main_skin_id, field_library_id)
  form = getForm(portal.portal_skins[main_skin_id], field_library_id)
  if form is None:
    # Field library has to be created
    modified_object_dict[form_path] = '1_create_form'
  else:
    field_library_dict = dict(('%s/%s' % (form_path, field.getId()), [])
                              for field in form.objectValues())
    # Check that proxy field are proxified to erp5_core
    for field in form.objectValues():
      # XXX Should check if this field is used as a template
      field_path = '%s/%s' % (form_path, field.getId())
      if field.meta_type == 'ProxyField':
        template_form_id = field.get_value('form_id')
        template_id = '%s/%s' % (template_form_id,
                                  field.get_value('field_id'))
        if field.getTemplateField() is None:
          modified_object_dict[field_path] = ('0_keep_dead_proxy_field',
                                              template_id)
        else:
          if template_form_id == field_library_id:
            field_library_dict['%s/%s' % (main_skin_id, template_id)] \
            .append(field_path)
          if template_form_id not in ('Base_viewFieldLibrary',
                                      field_library_id):
            modified_object_dict[field_path] = ('2_unproxify_field',
                                                template_id)
          elif field.delegated_list:
            # Found some delegated list
            modified_object_dict[field_path] = ('0_check_delegated_value',
                                                template_id)
      else:
        # Do not force proxification of field library field.
        # The nice developper probably have a good reason not to do it.
        modified_object_dict[field_path] = '0_keep_non_proxy_field'

for skin_folder_id in skin_id_list:
  skin_folder = context.portal_skins[skin_folder_id]
  # like erp5_project_trade
  alternate_skin_folder_id = skin_folder_id.replace(
                                     '_'.join(main_skin_id.split('_')[1:]), '')
  # like erp5_trade
  alternate_field_library_id = calculateFieldLibraryID(alternate_skin_folder_id)
  # like Base_viewTradeFieldLibrary
  # Find old field library to delete
  for object_id in skin_folder.objectIds():
    if (object_id.endswith('FieldLibrary') and \
        (object_id not in (field_library_id, 'Base_viewFieldLibrary',
                           alternate_field_library_id))):
      obj = getForm(skin_folder, object_id)
      if obj is None:
        raise KeyError, '%s/%s' % (skin_folder_id, object_id)
      elif obj.meta_type == 'ERP5 Form':
        modified_object_dict['%s/%s' % (skin_folder_id, object_id)] = \
                                                                  '4_delete_form'
      else:
        # Not an ERP5 Form, so, do nothing
        pass
    elif object_id == alternate_field_library_id:
      form_path = '%s/%s' % (skin_folder_id, object_id)
      form = getForm(portal.portal_skins[skin_folder_id], object_id)
      field_library_dict = dict(('%s/%s' % (form_path, field.getId()), [])
                              for field in form.objectValues())

  # Check all existing fields
  for form in skin_folder.objectValues():
    if form.meta_type in ('ERP5 Form', 'ERP5 Report'):
      form_id = form.getId()
      form_path = '%s/%s' % (skin_folder_id, form_id)

      if modified_object_dict.has_key(form_path):
        # The form is a Field Library
        if modified_object_dict[form_path] == '4_delete_form':
          # As the form will be deleted, no need to manage its fields
          pass
        else:
          raise KeyError, 'Unexpected form handling %s for %s' % \
              (modified_object_dict[form_path], form_path)
      elif form_id not in (field_library_id, alternate_field_library_id,
                           'Base_viewFieldLibrary',):
        # Check that proxy field are proxified to field library
        for field in form.objectValues():
          field_path = '%s/%s/%s' % (skin_folder_id, form_id, field.getId())
          if field.meta_type == 'ProxyField':
            template_form_id = field.get_value('form_id')
            template_id = '%s/%s' % (template_form_id,
                                      field.get_value('field_id'))
            if field.getTemplateField() is None:
              modified_object_dict[field_path] = ('0_keep_dead_proxy_field',
                                                  template_id)
            else:
              # XXX Only consider standard bt5 for now
              if template_form_id not in (field_library_id,
                                          alternate_field_library_id,
                                          'Base_viewFieldLibrary',):
                modified_object_dict[field_path] = ('2_unproxify_field',
                                                    template_id)
                # XXX Should proxify to a library's field
              else:
                key = '%s/%s' % (skin_folder_id, template_id)
                field_library_dict.setdefault(key, []).append(field_path)
                # Check that there is no delegated values
                if field.delegated_list:
                  # Found some delegated list
                  modified_object_dict[field_path] = (
                    '0_check_delegated_value', template_id)
          else:
            # Do not force proxification of field.
            # The nice developper probably have a good reason not to do it.
            modified_object_dict[field_path] = '0_keep_non_proxy_field'

for field_path, proxy_field_list in field_library_dict.items():
  if not proxy_field_list:
    modified_object_dict[field_path] = '0_unused_proxy_field'

i = 0
for key, value in modified_object_dict.items():
  line = newTempBase(context, 'tmp_install_%s' %(str(i)))
  if isinstance(value, tuple):
    value, template_id = value
  else:
    template_id = None
  if value.startswith('0_'):
    choice = []
  else:
    choice = [value]
  line.edit(
    object_id=key,
    template_id=template_id,
    choice=choice,
    choice_item_list=[[action_title_dict[value], value]],
  )
  line.setUid('new_%s' % key)
  field_list.append(line)
  i += 1

field_list.sort(key=lambda x:(x.choice_item_list[0][1], x.object_id))


return field_list
