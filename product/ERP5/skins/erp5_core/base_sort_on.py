##parameters=form_id,selection_name,field_sort_on,field_sort_order

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST


try:
  # No validation for now
  # Direct access to field (BAD)
  sort_on = []
  i = 0
  for k in field_sort_on:
    if k != 'None':
      v = field_sort_order[i]
      sort_on += [(k,v)]
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
