request = context.REQUEST

proxy_listbox_id = request.get('proxy_listbox_id', None)
if proxy_listbox_id is None:
  proxy_listbox_id = request.get('select_dialog', None)
if proxy_listbox_id is None:
  proxy_listbox_id = "Base_viewRelatedObjectListBase/listbox"

return proxy_listbox_id
