from Products.Formulator.Errors import FormValidationError

request=context.REQUEST


# Columns which occure more than once are replace by 'None'
# We do this because this causes problems everywhere and because
# in most cases, it is meaningless. 'None' elements will then be moved
# to the end of the list.

for x in range(len(field_columns)):
  if field_columns.count(field_columns[x]) > 1:
    field_columns[x] = 'None'
    stat_columns[x] = ' '


# The page template named "configure_list_dialog" displays first, columns in selection and then, those
# which are defined by default in the corresponding listbox properties. So field_columns
# and stat_columns may not be ordered the same way. So the script below sort the
# field_column list so as to have every 'None' at the end of the list


liste_none = []

def maj_liste_none():
  for x in range(len(field_columns)):
    if field_columns[x] == 'None':
      liste_none.append(x)


maj_liste_none()

for x in range(len(field_columns)):
  if len(liste_none) > 0 and field_columns[x] != 'None' and liste_none[0] < x:
    field_columns[liste_none[0]] = field_columns[x]
    stat_columns[liste_none[0]] = stat_columns[x]
    field_columns[x] = 'None'
    stat_columns[x] = ' '
    liste_none.pop(0)
    maj_liste_none()

# Now, we can try to save the selection


context.portal_selections.setSelectionStats(selection_name, stat_columns, REQUEST=request)

try:
  # No validation for now
  # Direct access to field (BAD)
  form = getattr(context,form_id)
  groups = form.get_groups()
  columns_dict = {}

  field = form.get_fields_in_group(groups[0])[0]
  columns = field.get_value('columns')
  all_columns = columns + [x for x in field.get_value('all_columns') if x not in columns]
  for (k, v) in [('None','None')] + all_columns:
    if k in field_columns and k != 'None':
      columns_dict[k] = v
  columns = []
  for k in field_columns:
    if k != 'None':
      columns += [(k ,  columns_dict[k])]
  context.portal_selections.setSelectionColumns(selection_name, columns, REQUEST=request)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)
else:
  redirect_url = context.portal_selections.getSelectionListUrlFor(selection_name)

request[ 'RESPONSE' ].redirect( redirect_url )
