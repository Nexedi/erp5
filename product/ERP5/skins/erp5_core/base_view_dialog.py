##parameters=form_id,cancel_url,dialog_method,selection_name,dialog_id,previous_md5_object_uid_list=None

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError
from string import join
from ZTUtils import make_query

request=context.REQUEST

#Exceptions for Workflow
if dialog_method == 'workflow_status_modify':
  return context.workflow_status_modify( form_id=form_id
                                       , dialog_id=dialog_id
                                       )
if dialog_method == 'base_list_ui':
  return context.base_list_ui( form_id=form_id
                             , selection_name=selection_name
                             , field_columns=getattr(request,'field_columns')
                             , stat_columns=getattr(request,'stat_columns')
                             )
if dialog_method == 'base_sort_on':
  return context.base_sort_on( form_id=form_id
                             , selection_name=selection_name
                             , field_sort_on=getattr(request,'field_sort_on')
                             , field_sort_order=getattr(request,'field_sort_order')
                             )

error_message = ''

try:
  # Validate the form
  form = getattr(context,dialog_id)
  form.validate_all_to_request(request)
  kw =  { 'form_id'             : form_id
        , 'selection_name'      : selection_name 
        , 'selection_index'     : None
        , 'dialog_id'           : dialog_id
        } # Missing selection_index
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
    listbox_keys = listbox.keys()
    listbox_keys.sort()
    for key in listbox_keys:
      listbox_line = listbox[key]
      listbox_line['listbox_key'] = key
      listbox_line_list.append(listbox[key])
    listbox_line_list = tuple(listbox_line_list)
    kw['listbox'] = listbox_line_list
    return getattr(context,dialog_method)(**kw)
  url_params_string = make_query(kw)
  # Check if the selection did not changed
  if previous_md5_object_uid_list is not None:
    selection_list = context.portal_selections.callSelectionFor(selection_name, context=context)
    if selection_list is not None:
      object_uid_list = map(lambda x:x.getObject().getUid(),selection_list)
      error = context.portal_selections.selectionHasChanged(previous_md5_object_uid_list,object_uid_list)
      if error:
        error_message = 'Sorry+your+selection+has+changed'
  url_params_string = make_query(**kw)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)

if error_message != '':
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                , 'portal_status_message=%s' % error_message
                                )
elif url_params_string != '':
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                            , dialog_method
                            , url_params_string
                            )
else:
  redirect_url = '%s/%s' % ( context.absolute_url()
                            , dialog_method
                            )

return request.RESPONSE.redirect( redirect_url )
