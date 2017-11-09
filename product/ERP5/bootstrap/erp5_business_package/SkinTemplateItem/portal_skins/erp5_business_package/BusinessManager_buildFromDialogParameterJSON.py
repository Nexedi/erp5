import json

# Load the JSON value for item_path_list
item_path_list = json.loads(item_path_list)

kwargs = {
  'checkNeeded': check_needed,
  'item_path_list': item_path_list}

context.build(**kwargs)

# XXX translate
return context.Base_redirect('view',keep_items={'portal_status_message': 'Built'})
