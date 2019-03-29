"""
  Save form on context.
"""
from json import dumps
from Products.Formulator.Errors import FormValidationError
from Products.CMFActivity.Errors import ActivityPendingError

request = context.REQUEST

# Prevent users who don't have rights to edit the object from
# editing it by calling the Base_edit script with correct
# parameters directly.
# XXX: implement it (above)

# Get the form
form = getattr(context,form_id)
edit_order = form.edit_order
try:
  # Validate
  form.validate_all_to_request(request, key_prefix=key_prefix)
except FormValidationError as validation_errors:
  # Pack errors into the request
  result = {}
  result['field_errors'] = {}
  field_errors = form.ErrorFields(validation_errors)
  for key, value in field_errors.items():
    result['field_errors'][key] = value.error_text
  return dumps(result)

(kw, encapsulated_editor_list), action = context.Base_edit(form_id, silent_mode=1)

context.log(kw)
context.edit(REQUEST=request, edit_order=edit_order, **kw)
for encapsulated_editor in encapsulated_editor_list:
  encapsulated_editor.edit(context)

# XXX: consider some kind of protocol ?
return dumps({})
