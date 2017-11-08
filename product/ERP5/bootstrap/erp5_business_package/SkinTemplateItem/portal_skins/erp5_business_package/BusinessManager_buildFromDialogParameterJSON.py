# Convert the item_path_list from str to list type
if isinstance(item_path_list, str):
  item_path_list = item_path_list.split(',')

kwargs = {
  'checkNeeded': check_needed,
  'item_path_list': item_path_list}

context.build(**kwargs)

# XXX translate
return context.Base_redirect('view',keep_items={'portal_status_message': 'Built'})
