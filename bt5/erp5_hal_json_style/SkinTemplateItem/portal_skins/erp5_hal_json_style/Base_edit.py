"""Handle form - REQUEST interaction.

-  Validate a form to the current REQUEST
-  Extract form data and editors from REQUEST,
-  Update current context with form data by calling edit or invoking editors

:param silent: int (0|1) means that the edit action is not invoked by a form
               submit but rather by an internal code thus the return value
               contains as much usefull info as possible

  TODO: split the generic form validation logic
  from the context update logic
"""
from Products.Formulator.Errors import FormValidationError
from Products.CMFActivity.Errors import ActivityPendingError

request=container.REQUEST
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
edit_order = form.edit_order

# Prevent users who don't have rights to edit the object from
# editing it by calling the Base_edit script with correct
# parameters directly.
if not silent_mode and not request.AUTHENTICATED_USER.has_permission('Modify portal content', context):
  request.RESPONSE.setStatus(403)
  return context.ERP5Document_getHateoas(form=form, REQUEST=request, mode='form')

try:
  # Validate
  form.validate_all_to_request(request, key_prefix=key_prefix)
except FormValidationError as validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  # Make sure editors are pushed back as values into the REQUEST object
  for f in form.get_fields():
    field_id = f.id
    if request.has_key(field_id):
      value = request.get(field_id)
      if callable(value):
        value(request)
  if silent_mode:
    return context.ERP5Document_getHateoas(form=form, REQUEST=request, mode='form'), 'form'
  request.RESPONSE.setStatus(400)
  return context.ERP5Document_getHateoas(form=form, REQUEST=request, mode='form')


def editListBox(listbox_field, listbox):
  """Go through every item in the listbox and call its `edit` with modified values."""
  if listbox is None:
    return

  # extract hidden (global) attributes from request to be used in listbox's update
  global_attr = {hidden_key: getattr(request, hidden_key, None)
                 for hidden_key, _ in listbox_field.get_value('global_attributes')} \
                if listbox_field.has_value('global_attributes') \
                else {}

  for item_url, item_value in listbox.items():
    item_value.update(global_attr)
    # Form: '' -> ERP5: None
    editor_list = []
    value_dict = {}
    for key, value in item_value.items():
      # for every value decide whether it is an attribute or an editor
      if hasattr(value, 'edit'):
        editor_list.append(value)
      else:
        value_dict[key] = value if value != '' else None

    if value_dict:
      if listbox_edit is None:
        obj = context.restrictedTraverse(item_url)
        obj.edit(edit_order=edit_order, **value_dict)
        for editor in editor_list:
          editor.edit(obj)
      else:
        listbox_edit(item_url, edit_order, value_dict)


def editMatrixBox(matrixbox_field, matrixbox):
  """ Function called to edit a Matrix box
  """
  if matrixbox is None:
    return

  cell_base_id = matrixbox_field.get_value('cell_base_id')
  portal_type = matrixbox_field.get_value('cell_portal_type')
  getter_method = matrixbox_field.get_value('getter_method')
  if getter_method not in (None, ''):
    matrix_context = getattr(context,getter_method)()
  else:
    matrix_context = context

  if matrix_context is None:
    return

  kd = {}
  kd['portal_type'] = portal_type
  kd['base_id'] = cell_base_id
  gv = {}
  if matrixbox_field.has_value('global_attributes'):
    hidden_attributes = [x[0] for x in matrixbox_field.get_value('global_attributes')]
    for k in hidden_attributes:
      gv[k] = getattr(request, k, None)
  if matrixbox_field.get_value('update_cell_range'):
    as_cell_range_script_id = matrixbox_field.get_value(
            'as_cell_range_script_id')
    lines = []
    columns = []
    tabs = []
    extra_dimension_list_list = []
    if as_cell_range_script_id:
      cell_range = getattr(matrix_context,
          as_cell_range_script_id)(matrixbox=True, base_id=cell_base_id)
      if len(cell_range) == 1:
        lines, = cell_range
      elif len(cell_range) == 2:
        lines, columns = cell_range
      elif len(cell_range) == 3:
        lines, columns, tabs = cell_range
      elif len(cell_range) > 3:
        lines = cell_range[0]
        columns = cell_range[1]
        tabs = cell_range[2]
        extra_dimension_list_list = cell_range[3:]
    else:
      lines = matrixbox_field.get_value('lines')
      columns = matrixbox_field.get_value('columns')
      tabs = matrixbox_field.get_value('tabs')

    column_ids = [x[0] for x in columns]
    line_ids = [x[0] for x in lines]
    tab_ids = [x[0] for x in tabs]
    extra_dimension_category_list_list = [[category for category, _ in dimension_list] for dimension_list in extra_dimension_list_list]

    # There are 3 cases
    # Case 1: we do 1 dimensional matrix
    # Case 2: we do 2 dimensional matrix
    # Case 3: we do 2 dimensional matrix + tabs
    # Case 4: we do 2 dimensional matrix + tabs + extra
    cell_range = matrix_context.getCellRange(base_id = cell_base_id)
    if (len(column_ids) == 0) or (column_ids[0] is None):
      matrixbox_cell_range = [line_ids]
      if cell_range != matrixbox_cell_range:
        matrix_context.setCellRange(line_ids, base_id=cell_base_id)

    elif (len(tab_ids) == 0) or (tab_ids[0] is None):
      matrixbox_cell_range = [line_ids, column_ids]
      if cell_range != matrixbox_cell_range:
        matrix_context.setCellRange(line_ids, column_ids, base_id=cell_base_id)

    else:
      matrixbox_cell_range = [line_ids, column_ids, tab_ids]
      if extra_dimension_category_list_list:
        matrixbox_cell_range = matrixbox_cell_range + extra_dimension_category_list_list
      if cell_range != matrixbox_cell_range:
        matrix_context.setCellRange(base_id=cell_base_id, *matrixbox_cell_range)

  for cell_index_tuple, cell_value_dict in matrixbox.items():
    # Only update cells which still exist
    if not matrix_context.hasInRange(*cell_index_tuple, **kd):
      return "Cell %s does not exist" % str(cell_index_tuple)

    cell = matrix_context.newCell(*cell_index_tuple, **kd)
    if cell is None:
      return "Could not create cell %s" % str(cell_index_tuple)

    cell.edit(edit_order=edit_order, **gv)  # First update globals which include the def. of property_list
    if cell_value_dict.has_key('variated_property'):
      # For Variated Properties
      value = cell_value_dict['variated_property']
      del cell_value_dict['variated_property']
      if gv.has_key('mapped_value_property_list'):
        # Change the property which is defined by the
        # first element of mapped_value_property_list
        # XXX Kato: What? Why?
        # XXX May require some changes with Sets
        key = gv['mapped_value_property_list'][0]
        cell_value_dict[key] = value
    # Form: '' -> ERP5: None
    cleaned_v = cell_value_dict.copy()
    for key, value in cleaned_v.items():
      if value == '':
        cleaned_v[key] = None
    cell.edit(edit_order=edit_order, **cleaned_v) # and update the cell specific values


edit_kwargs = {}  # keyword arguments for `edit` function on context
encapsulated_editor_list = []  # editors placed inside REQUEST object
MARKER = []  # placeholder for an empty value
message = Base_translateString("Data updated.")

try:
  # extract all listbox's object form fields from the request and `edit` the object
  for field in form.get_fields():
    # Dispatch field either to `edit_kwargs` (in case of simple fields) or to `encapsulated_editor_list` in case of editors
    field_name = field.id if not field.has_value('alternate_name') else (field.get_value('alternate_name') or field.id)
    field_value = getattr(request, field_name, MARKER)
    if hasattr(field_value, 'edit'):
      # field is an encapsulated editor; call it later
      encapsulated_editor_list.append(field_value)
    elif field_value is not MARKER and field_name.startswith(field_prefix):
      # object own attribute (fix value Form: '' -> ERP5: None)
      edit_kwargs[field_name[len(field_prefix):]] = field_value if field_value != '' else None

    ## XXX We need to find a way not to use meta_type.
    field_meta_type = field.meta_type
    if field_meta_type == 'ProxyField':
      field_meta_type = field.getRecursiveTemplateField().meta_type

    if(field_meta_type == 'ListBox'):
      editListBox(field, request.get(field.id))
    if(field_meta_type == 'MatrixBox'):
      editMatrixBox(field, request.get(field.id))

  # Return parsed values 
  if silent_mode:
    return (edit_kwargs, encapsulated_editor_list), 'edit'

  # Maybe we should build a list of objects we need
  # Update basic attributes
  context.edit(REQUEST=request, edit_order=edit_order, **edit_kwargs)
  for encapsulated_editor in encapsulated_editor_list:
    encapsulated_editor.edit(context)
except ActivityPendingError as e:
  message = Base_translateString(str(e))

if message_only:
  return message

ignore_layout = int(ignore_layout)
editable_mode = int(editable_mode)
spp = context.getPhysicalPath()
spp =list(spp)
s_url = request["SERVER_URL"]
spp.insert(0,s_url)

# for web mode, we should use 'view' instead of passed form_id
# after 'Save & View'.
if context.REQUEST.get('is_web_mode', False) and \
    not editable_mode:
  form_id = 'view'

# Directly render the form after a successful edit, but in a before commit
# hook, so that if interactions modify the state we render the new state.

# Cleanup formulator's special key in request to ensure field are only calculated from context and not the request anymore
for key in list(context.REQUEST.keys()):
  if str(key).startswith('field') or str(key).startswith('subfield'):
    context.REQUEST.form.pop(key, None)
return context.Base_renderFormAtEndOfTransaction(request, request.response, form_id, message=message)
