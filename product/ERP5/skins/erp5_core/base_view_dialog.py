##parameters=form_id,cancel_url,dialog_method,selection_name,dialog_id

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError
from string import join
from ZTUtils import make_query

request=context.REQUEST

#Exceptions for Workflow
if dialog_method == 'workflow_status_modify':
  return context.workflow_status_modify(form_id=form_id,
                                        dialog_id=dialog_id
                                        )


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
  # Object view params
  kw['form_id'] = form_id
  kw['dialog_id'] = dialog_id
  kw['selection_name'] = selection_name
  url_params_string = make_query(**kw)
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
