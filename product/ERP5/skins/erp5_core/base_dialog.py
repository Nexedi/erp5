##parameters=form_id,cancel_url,dialog_method,selection_name,dialog_id,**kw

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError
from string import join
from ZTUtils import make_query

request=context.REQUEST

#Exceptions for UI and Sort
if dialog_method == 'base_list_ui':
  return context.base_list_ui(form_id=form_id,
                              selection_name=selection_name,
                              field_columns=getattr(request,'field_columns'),
                              stat_columns=getattr(request,'stat_columns'))
if dialog_method == 'base_sort_on':
  return context.base_sort_on(form_id=form_id,
                              selection_name=selection_name,
                              field_sort_on=getattr(request,'field_sort_on'),
                              field_sort_order=getattr(request,'field_sort_order'))

try:
  # Validate the form
  form = getattr(context,dialog_id)
  form.validate_all_to_request(request)
  kw = {'form_id': form_id, 'selection_name': selection_name , 'selection_index': None} # Missing selection_index
  has_listbox = 0
  for f in form.get_fields():
    k = f.id
    v = getattr(request,k,None)
    if v is not None:
      if k[0:3] == 'my_':
        k = k[3:]
        kw[k] = v
      elif k in ('import_file', 'listbox'):
        if f.meta_type == 'ListBox': has_listbox = 1
        kw[k] = v
  # Add some properties required by UI
  kw['cancel_url'] = cancel_url
  # Redirect if possible, or call directly else
  if kw.has_key('import_file'):
    # We can not redirect if we do an import
    import_file = kw['import_file']
    return getattr(context,dialog_method)(**kw)
  if has_listbox:
    listbox_line_list = []
    listbox = getattr(request,'listbox',None)
    for key in listbox.keys():
      listbox_line = listbox[key]
      listbox_line['listbox_key'] = key
      listbox_line_list.append(listbox[key])
    listbox_line_list = tuple(listbox_line_list)
    kw['listbox'] = listbox_line_list
    return getattr(context,dialog_method)(**kw)
  url_params_string = make_query(kw)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)

if url_params_string != '':
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                            , dialog_method
                            , url_params_string
                            )
else:
  redirect_url = '%s/%s' % ( context.absolute_url()
                            , dialog_method
                            )

return request.RESPONSE.redirect( redirect_url )
