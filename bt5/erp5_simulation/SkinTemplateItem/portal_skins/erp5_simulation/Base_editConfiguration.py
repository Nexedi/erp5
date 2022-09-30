# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base
#
# TODO
#   - Implement validation of matrix fields
#   - Implement validation of list fields
#
from Products.ERP5Type.Message import translateString
from Products.Formulator.Errors import FormValidationError

request=context.REQUEST

try:
  # Define form basic fields
  form = getattr(context,form_id)
  # Validate
  form.validate_all_to_request(request)
  # Basic attributes
  kw = {}
  # Parse attributes
  for f in form.get_fields():
    k = f.id
    v = getattr(request,k,None)
    if v is not None:
      if k[0:3] == 'my_':
        # We only take into account
        # the object attributes
        k = k[3:]
        if getattr(v, 'as_dict'): # FormBox
          kw.update(v.as_dict())
        else:
          kw[k] = v
  # Update basic attributes
  context.updateConfiguration(**kw)
  context.reindexObject()
except FormValidationError as validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)

# for web mode, we should use 'view' instead of passed form_id
# after 'Save & View'.
if request.get('is_web_mode', False) and not editable_mode:
  form_id = 'view'

return context.Base_redirect(form_id,
  keep_items=dict(portal_status_message=translateString('Data Updated.')))
