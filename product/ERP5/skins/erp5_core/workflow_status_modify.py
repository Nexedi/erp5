##parameters=form_id,dialog_id

from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST
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
  toto = context.portal_workflow.doActionFor(
      context,
      kw['workflow_action'],
      **kw)
  #return str(toto)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)
except ValueError, value_error:
  # Pack errors into the request
  redirect_url = '%s/%s?%s%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=',value_error
                                  )

  context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
else:
  # We will check if there's an error_message
  history_data = None
  try:
    history_data = context.portal_workflow.getInfoFor(ob=context.getObject(), name='history')
  except:
    pass
  redirect_url = None
  if history_data is not None:
    last_history_data = history_data[len(history_data)-1]
    error_message = last_history_data.get('error_message')
    if error_message != None and error_message != '':
      redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=%s' % error_message
                                  )
      pass
  if redirect_url is None:
    redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=Status+changed.'
                                  )

  context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
