##parameters=form_id='', selection_index='', selection_name='', list_method_id=None
from ZTUtils import make_query

request = context.REQUEST

#return request

if list_method_id:
  kw = { 'selection_index': selection_index,
         'selection_name': selection_name,
         'list_method_id': list_method_id,
        }
else:
  kw = { 'selection_index': selection_index,
         'selection_name': selection_name,
        }

if list_method_id:
  try:
    # Define form basic fields
    form = getattr(context,form_id)
    listbox_field = None
    # Search listbox
    for f in form.get_fields():
      if f.meta_type == "ListBox":
        listbox_field = f
        break
    # Lookup listbox search cols
    for col_id, col_title in listbox_field.get_value('search_columns'):
      # Left is col_id
      v = request.form.get(col_id, '')
      kw[col_id] = v
    # Redirect
    request.RESPONSE.redirect('%s/%s?%s' % (context.absolute_url(), form_id, make_query(kw)))
  except:
    # Default behaviour is not as great but returns something
    return getattr(context,form_id)(request)
else:
  # Default behaviour is not as great but returns something
  kw.update(request.form)
  if kw.has_key('listbox_uid'): del kw['listbox_uid']
  if kw.has_key('list_start'): del kw['list_start']
  request.RESPONSE.redirect('%s/%s?%s' % (context.absolute_url(), form_id, make_query(kw)))
  #return getattr(context,form_id)(request)
