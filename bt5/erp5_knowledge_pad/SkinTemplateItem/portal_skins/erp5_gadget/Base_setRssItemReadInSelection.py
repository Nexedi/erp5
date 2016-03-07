portal_selection = getattr(context,'portal_selections')
params = portal_selection.getSelectionParamsFor(selection_name)
rss_read_item_list = params.get('rss_read_item_list', [])
params['rss_read_item_list'] = rss_read_item_list
if item not in rss_read_item_list:
  rss_read_item_list.append(item)
portal_selection.setSelectionParamsFor(selection_name, params)
return item
