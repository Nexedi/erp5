## Script (Python) "Base_callDialogMethod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,cancel_url,dialog_method,selection_name,dialog_id,enable_pickle=0,**kw
##title=
##
# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError
from string import join
from ZTUtils import make_query

request=context.REQUEST

#Exceptions for UI and Sort
if dialog_method == 'Base_configureUI':
  return context.Base_configureUI(form_id=form_id,
                              selection_name=selection_name,
                              field_columns=getattr(request,'field_columns'),
                              stat_columns=getattr(request,'stat_columns'))
if dialog_method == 'Base_configureSortOn':
  return context.Base_configureSortOn(form_id=form_id,
                              selection_name=selection_name,
                              field_sort_on=getattr(request,'field_sort_on'),
                              field_sort_order=getattr(request,'field_sort_order'))

try:
  # Validate the form
  kw = {}
  if request.has_key('pickle_string'):
    pickle_string = request.get('pickle_string')
    kw = context.portal_selections.getObjectFromPickle(pickle_string)
  #kw = context.portal_selections.getCookieInfo(request,dialog_id)
  if kw != {}:
    form = getattr(context.asContext(context=None,portal_type=context.getPortalType(),**kw),dialog_id)
  else:
    form = getattr(context,dialog_id)
  #return context.REQUEST
  #return kw
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
  md5_object_uid_list = getattr(request,'md5_object_uid_list',None)
  kw['md5_object_uid_list'] = md5_object_uid_list
  kw['cancel_url'] = cancel_url
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
  if enable_pickle or (form.update_action!=''):
    pickle_string = context.portal_selections.getPickle(**kw)
    request.set('pickle_string', pickle_string)
  # Redirect if possible, or call directly else
  if kw.has_key('import_file'):
    # We can not redirect if we do an import
    import_file = kw['import_file']
    return getattr(context,dialog_method)(**kw)
  if has_listbox:
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
