## Script (Python) "Base_searchHandler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,dialog_id,list_form_id,list_method_id=''
##title=
##
from Products.Formulator.Errors import ValidationError, FormValidationError
from ZTUtils import make_query

request=context.REQUEST

module_name = context.getId()

try:
  # Validate the form
  form = getattr(context,dialog_id)
  form.validate_all_to_request(request)
  kw = {}
  for f in form.get_fields():
    k = f.id
    k = k[3:]
    v = getattr(request,k,None)
    if v is not None and k != 'list_form_id' :
      kw[k] = v
    if list_method_id is not None and list_method_id  != '' :
      kw['list_method_id'] = list_method_id
  url_params_string = make_query(kw)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)

if url_params_string != '':
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                            , list_form_id
                            , url_params_string
                            )
else:
  redirect_url = '%s/%s' % ( context.absolute_url()
                            , list_form_id
                            )

return request.RESPONSE.redirect( redirect_url )
