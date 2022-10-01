from Products.ERP5Type.Message import translateString
from Products.Formulator.Errors import FormValidationError
request = container.REQUEST

form = getattr(context, form_id)
try:
  # Validate
  form.validate_all_to_request(request, key_prefix='my_')
except FormValidationError as validation_errors:
  # Pack errors into the request
  result = {}
  result['field_errors'] = {}
  field_errors = form.ErrorFields(validation_errors)
  for key, value in field_errors.items():
    result['field_errors'][key] = value.error_text
  return form()

(kw, encapsulated_editor_list), _ = context.Base_edit(form_id, silent_mode=1)
assert not encapsulated_editor_list

context.setProperties(
  title=kw['title'],
  description=kw['description'],
  manager_bypass=context.manager_bypass)
marker = []
if context.getProperty("jsplumb_graph", marker) is marker:
  context.manage_setProperty("jsplumb_graph", kw["jsplumb_graph"])
else:
  context.manage_changeProperties({'jsplumb_graph': kw["jsplumb_graph"]})

# XXX handle workflow edition here.

return context.Base_redirect(form_id,
                             keep_items={'portal_status_message': translateString("Data updated.")})
