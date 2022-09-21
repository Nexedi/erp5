from Products.Formulator.Errors import FormValidationError
from Products.ERP5Type.Utils import convertToUpperCase

request=container.REQUEST
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

message = Base_translateString("Data updated.")

# Extra security
if request.get('field_prefix', None):
  field_prefix = 'my_' # Prevent changing the prefix through publisher

# Use dialog_id if present, otherwise fall back on form_id.
if dialog_id not in ('', None):
  form_id = dialog_id

# Prevent users who don't have rights to edit the object from
# editing it by calling the Base_edit script with correct
# parameters directly.
if not silent_mode and not request.AUTHENTICATED_USER.has_permission('Modify portal content', context) :
  msg = Base_translateString("You do not have the permissions to edit the object.")
  redirect_url = '%s/%s?selection_index=%s&selection_name=%s&%s' % (context.absolute_url(), form_id, selection_index, selection_name, 'portal_status_message=%s' % msg)
  return request['RESPONSE'].redirect(redirect_url)

# Get the form
form = getattr(context,form_id)

try:
  # Validate
  form.validate_all_to_request(request)
except FormValidationError, validation_errors:
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
  if silent_mode: return form(request), 'form'
  return form(request)


def updateTranslation():

  property_list = context.Base_getContentTranslationPropertyValueAndLabelList()
  language_list = context.Base_getContentTranslationLanguageValueAndLabelList()

  def upperCase(text):
    return convertToUpperCase(text.replace('-', '_'))

  for key in request.form.keys():
    if key.startswith('field_matrixbox_'):
      property_index, language_index = map(int, key.split('_')[-3:-1])
      value = request.form.get(key)
      property_name = property_list[property_index][0]
      language = language_list[language_index][0]
      setter = getattr(context, 'set%s' % upperCase('%s_translated_%s' % (language, property_name)))
      setter(value)


context.edit()#invoke interaction workflows etc.
updateTranslation()

ignore_layout = int(ignore_layout)
editable_mode = int(editable_mode)
redirect_url = '%s/%s?ignore_layout:int=%s&editable_mode:int=%s&portal_status_message=%s' % (
  context.absolute_url(),
  form_id,
  ignore_layout,
  editable_mode,
  message)

result = request['RESPONSE'].redirect(redirect_url) 

if silent_mode:
  return result, 'redirect'
return result
