from Products.Formulator.Errors import FormValidationError

request = context.REQUEST
field_sort_type = request.form.get('field_sort_type', None)
form = context.Folder_viewSortOnDialog

try:
  # No validation for now
  # Direct access to field (BAD)
  sort_on = []
  i = 0
  for k in field_sort_on:
    if k != 'None':
      if field_sort_type is None:
        v = field_sort_order[i]
        sort_on += [(k,v)]
      else:
        v = field_sort_order[i]
        t = field_sort_type[i]
        sort_on += [(k, v, t)]
    i += 1
  context.portal_selections.setSelectionSortOrder(selection_name, sort_on)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)
else:
  redirect_url = context.portal_selections.getSelectionListUrlFor(selection_name)

request[ 'RESPONSE' ].redirect( redirect_url )
