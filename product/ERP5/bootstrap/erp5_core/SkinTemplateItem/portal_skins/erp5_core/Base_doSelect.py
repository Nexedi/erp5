from ZTUtils import make_query

request = context.REQUEST

#return request

context.Base_updateListboxSelection()

kw = { 'selection_index': selection_index,
       'selection_name': selection_name,
      }

# Default behaviour is not as great but returns something
kw.update(request.form)

if kw.has_key('listbox_uid'): del kw['listbox_uid']
if kw.has_key('list_start'): del kw['list_start']

if request.form.has_key('dialog_id'):
  form_id = request.form['dialog_id']
else:
  form_id = request.form['form_id']

url_params_string = make_query(kw)

if len(url_params_string) > 2000:
  # If we cannot redirect, then call the form directly.
  return getattr(context, form_id)(**kw)

request.RESPONSE.redirect('%s/%s?%s' % (context.absolute_url(), form_id, url_params_string))
