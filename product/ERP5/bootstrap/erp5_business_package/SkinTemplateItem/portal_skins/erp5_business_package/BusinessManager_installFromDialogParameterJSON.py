context.getParentValue().installBusinessItemList([context], item_path_list)

# XXX translate
return context.Base_redirect('view',keep_items={'portal_status_message': 'Done'})
