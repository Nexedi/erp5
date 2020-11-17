from Products.Formulator.Errors import FormValidationError
from Products.CMFActivity.Errors import ActivityPendingError

request=context.REQUEST
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

# Extra security
if request.get('field_prefix', None):
  field_prefix = 'my_' # Prevent changing the prefix through publisher

# Use dialog_id if present, otherwise fall back on form_id.
if dialog_id not in ('', None):
  form_id = dialog_id

# Get the form
form = getattr(context,form_id)

try:
  # Validate
  form.validate_all_to_request(request)
except FormValidationError as validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  # Make sure editors are pushed back as values into the REQUEST object
  for f in form.get_fields():
    field_id = f.id
    if field_id in request:
      value = request.get(field_id)
      if callable(value):
        value(request)
  return form(request)

# Some initilizations
kw = {}
encapsulated_editor_list = []
MARKER = []
message = Base_translateString("Data updated.")


def parseField(f):
  """
   Parse given form field, to put them in
   kw or in encapsulated_editor_list
  """
  k = f.id
  v = getattr(request, k, MARKER)
  if hasattr(v, 'edit'):
    # This is an encapsulated editor
    # call it
    encapsulated_editor_list.append(v)
  elif v is not MARKER:
    if k.startswith(field_prefix):
      # We only take into account
      # the object attributes
      k = k[len(field_prefix):]
      # Form: '' -> ERP5: None
      if v == '':
        v = None
      kw[k] = v

try:
  # We process all the field in form and
  # we check if they are in the request,
  # then we edit them
  for field in form.get_fields():
    parseField(field)

  for encapsulated_editor in encapsulated_editor_list:
    encapsulated_editor.edit(context)
except ActivityPendingError as e:
  message = Base_translateString("%s" % e)

ignore_layout = int(ignore_layout)
editable_mode = int(editable_mode)

if not selection_index:
  redirect_url = '%s/%s?ignore_layout:int=%s&editable_mode:int=%s&portal_status_message=%s' % (
                                  context.absolute_url(),
                                  form_id,
                                  ignore_layout,
                                  editable_mode,
                                  message)
else:
  redirect_url = '%s/%s?selection_index=%s&selection_name=%s&ignore_layout:int=%s&editable_mode=%s&portal_status_message=%s' % (
                              context.absolute_url(),
                              form_id,
                              selection_index,
                              selection_name,
                              ignore_layout,
                              editable_mode,
                              message)

return request['RESPONSE'].redirect(redirect_url)
