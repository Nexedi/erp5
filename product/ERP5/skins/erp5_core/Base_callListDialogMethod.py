## Script (Python) "Base_callListDialogMethod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,cancel_url,dialog_method,selection_name,dialog_id
##title=
##
# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError
from string import join

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
if dialog_method == 'Base_updateRelation':
  return context.Base_updateRelation(form_id=form_id,
                              field_id=request.get('field_id'),
                              selection_name=selection_name,
                              selection_index=request.get('selection_index'),
                              object_uid=request.get('object_uid'),
                              uids=request.get('uids'),
                              listbox_uid=request.get('listbox_uid'))
if dialog_method == 'Base_createRelation':
  return context.Base_createRelation(form_id=form_id,
                              selection_name=selection_name,
                              selection_index=request.get('selection_index'),
                              base_category=request.get('base_category'),
                              object_uid=request.get('object_uid'),
                              catalog_index=request.get('catalog_index'),
                              default_module=request.get('default_module'),
                              dialog_id=dialog_id,
                              portal_type=request.get('portal_type'),
                              return_url=request.get('cancel_url'))
if dialog_method == 'Folder_delete':
  return context.Folder_delete(form_id=form_id,
                              field_id=request.get('field_id'),
                              selection_name=selection_name,
                              selection_index=request.get('selection_index'),
                              object_uid=request.get('object_uid'),
                              uids=request.get('listbox_uid'),
                              md5_object_uid_list=request.get('md5_object_uid_list'),
                              cancel_url=request.get('cancel_url'))

try:
  # Validate the form
  form = getattr(context,dialog_id)
  form.validate_all_to_request(request)
  kw = {}
  for f in form.get_fields():
    k = f.id
    v = getattr(request,k,None)
    if v is not None:
      k = k[3:]
      kw[k] = v
  url_params = []
  for (k,v) in kw.items():
    url_params += ['%s=%s' % (k,v)]
  url_params_string = join(url_params, '&')
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
