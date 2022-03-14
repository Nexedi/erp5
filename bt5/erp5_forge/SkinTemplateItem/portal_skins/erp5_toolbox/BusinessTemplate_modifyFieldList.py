listbox_line_list = list(listbox)
listbox_line_list.sort(key=lambda x: (x['choice'], x['listbox_key']))

for listbox_line in listbox_line_list:
  choice = listbox_line['choice']
  key = listbox_line['listbox_key']

  if not choice:
    continue
  elif len(choice) > 1:
    raise ValueError('Unknown choice %s' % choice)
  else:
    choice = choice[0]
    if choice.startswith('0_'):
      continue
    elif choice == '1_create_form':
      skin_folder_id, form_id = key.split('/')
      skin_folder = context.portal_skins[skin_folder_id]
      skin_folder.manage_addProduct['ERP5Form'].addERP5Form(id=form_id, title='')
    elif choice == '2_unproxify_field':
      key_list = key.split('/')
      form_path, field_id = '/'.join(key_list[:-1]), key_list[-1]
      form = context.portal_skins.restrictedTraverse(form_path)
      form.unProxifyField({field_id: None})
    elif choice == '4_delete_form':
      skin_folder_id, form_id = key.split('/')
      skin_folder = context.portal_skins[skin_folder_id]
      skin_folder.manage_delObjects([form_id])
      # skin_folder.manage_addProduct['ERP5Form'].addERP5Form(id=form_id, title='')
      # raise NotImplementedError
    else:
      raise ValueError('Unknown choice %s' % choice)

context.Base_redirect()
