form = getattr(context, form_id)

request = REQUEST or context.REQUEST

# HAL JSON uses HTTP codes to communicate what the payload represents
if request.get('field_errors', None):
  # HTTP400 means invalid form
  request.RESPONSE.setStatus(400)

return context.ERP5Document_getHateoas(form=form, mode='form')
