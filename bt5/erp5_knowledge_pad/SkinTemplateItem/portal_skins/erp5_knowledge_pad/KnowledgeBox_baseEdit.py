"""
  This script edits a Knowledge Box instance used for saving a Gadget preferences.
"""
from Products.Formulator.Errors import FormValidationError
from json import dumps

kw = {}
request = context.REQUEST
form = request.form
fields = filter(lambda x: x.startswith(form_fields_main_prefix), form.keys())
box = context.restrictedTraverse(box_relative_url)
portal_selection = context.getPortalObject().portal_selections

# do validation
form = getattr(box, form_id)
try:
  # Validate
  form.validate_all_to_request(request, key_prefix=form_fields_main_prefix)
except FormValidationError as validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  # we need form rendered in gadget mode
  request.set('is_gadget_mode', 1)
  # Make sure editors are pushed back as values into the REQUEST object
  for f in form.get_fields():
    field_id = f.id
    if field_id in request:
      value = request.get(field_id)
      if callable(value):
        value(request)
  # return validation failed code and rendered form
  result = {'content': form(request, key_prefix=form_fields_main_prefix),
            'validation_status':  0}
  return dumps(result)

form = request.form
# get interesting for us fields and save
listbox_selection_field_prefix = '%s_my_listbox_selection_' %form_fields_main_prefix
for field in fields:
  #if it's a fied in a lisbox gadget it modifies directly the selection
  if field.startswith(listbox_selection_field_prefix):
    selection_name = context.Base_getListboxGadgetSelectionName(box_relative_url)
    selection = portal_selection.getSelectionFor(selection_name)
    if selection is not None:
      params =  selection.getParams()
      params[field.replace(listbox_selection_field_prefix, '')] = str(form[field])
      portal_selection.setSelectionParamsFor(selection_name, params)
  kw[field.replace('%s_my_' %form_fields_main_prefix, '')] = form[field]

# edit
box.edit(**kw)

if not synchronous_mode:
  # return JSON in asynchronous mode
  result = {'content': '',
            'validation_status': 1}
  return dumps(result)

# determine redirect URL as passed from gadget preference form
if gadget_redirect_url is None:
  # taking URL1 as the base of the original URL.
  # it works for both synchronous and  asynchronous gadgets
  gadget_redirect_url = request['URL1']
request.RESPONSE.redirect('%s?portal_status_message=%s'
                           %(gadget_redirect_url,
                             context.Base_translateString('Preference updated.')))
