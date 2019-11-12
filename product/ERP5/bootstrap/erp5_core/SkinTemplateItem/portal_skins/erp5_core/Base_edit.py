"""
  This script validates a form to the current REQUEST,
  processes the REQUEST to extract form data and editors,
  then updates the current context with the form data
  by calling edit on it or by invoking editors.

  TODO: split the generic form validation logic
  from the context update logic
"""
from Products.Formulator.Errors import FormValidationError
from ZTUtils import make_query

request=container.REQUEST
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

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
edit_order = form.edit_order

try:
  # Validate
  form.validate_all_to_request(request, key_prefix=key_prefix)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  # Make sure editors are pushed back as values into the REQUEST object
  for field in form.get_fields():
    field_id = field.id
    if request.has_key(field_id):
      value = request.get(field_id)
      if callable(value):
        value(request)
  if silent_mode: return form(request), 'form'
  return form(request)

def editListBox(listbox_field, listbox):
  """ Function called to edit a listbox
  """
  if listbox is not None:
    global_property_dict = {}
    if listbox_field.has_value('global_attributes'):
      hidden_attribute_list = map(lambda x:x[0], listbox_field.get_value('global_attributes'))
      for hidden_attribute in hidden_attribute_list:
        global_property_dict[hidden_attribute] = getattr(request, hidden_attribute, None)
    for item_url, listbox_item_dict in listbox.items():
      listbox_item_dict.update(global_property_dict)
      # Form: '' -> ERP5: None
      encapsulated_editor_list = []
      cleaned_v = {}
      for key, value in listbox_item_dict.items():
        if hasattr(value, 'edit'):
          encapsulated_editor_list.append(value)
        else:
          if value == '':
            value = None
          cleaned_v[key] = value

      if cleaned_v:
        if listbox_edit is None:
          obj = context.restrictedTraverse(item_url)
          obj.edit(edit_order=edit_order, **cleaned_v)
        else:
          listbox_edit(item_url, edit_order, cleaned_v)

      for encapsulated_editor in encapsulated_editor_list:
        encapsulated_editor.edit(obj)

def editMatrixBox(matrixbox_field, matrixbox):
  """ Function called to edit a Matrix box
  """
  if matrixbox is not None:
    cell_base_id = matrixbox_field.get_value('cell_base_id')
    portal_type = matrixbox_field.get_value('cell_portal_type')
    getter_method = matrixbox_field.get_value('getter_method')
    if getter_method not in (None, ''):
      matrix_context = getattr(context,getter_method)()
    else:
      matrix_context = context
    if matrix_context is not None:
      k_dict = {}
      k_dict['portal_type'] = portal_type
      k_dict['base_id'] = cell_base_id
      global_property_dict = {}
      if matrixbox_field.has_value('global_attributes'):
        hidden_attribute_list = [x[0] for x in matrixbox_field.get_value('global_attributes')]
        for hidden_attribute in hidden_attribute_list:
          global_property_dict[hidden_attribute] = getattr(request, hidden_attribute, None)
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

        column_ids = map(lambda x: x[0], columns)
        line_ids = map(lambda x: x[0], lines)
        tab_ids = map(lambda x: x[0], tabs)
        extra_dimension_category_list_list = [[category for category, label in dimension_list] for dimension_list in extra_dimension_list_list]

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

      for cell_index_tuple, cell_dict in matrixbox.items():
        # Only update cells which still exist
        if matrix_context.hasInRange(*cell_index_tuple, **k_dict):
          cell = matrix_context.newCell(*cell_index_tuple, **k_dict)
          if cell is not None:
            cell.edit(edit_order=edit_order, **global_property_dict)  # First update globals which include the def. of property_list
            if cell_dict.has_key('variated_property'):
              # For Variated Properties
              variated_property = cell_dict['variated_property']
              del cell_dict['variated_property']
              if global_property_dict.has_key('mapped_value_property_list'):
                # Change the property which is defined by the
                # first element of mapped_value_property_list
                # XXX May require some changes with Sets
                key = global_property_dict['mapped_value_property_list'][0]
                cell_dict[key] = variated_property
            # Form: '' -> ERP5: None
            cleaned_v = cell_dict.copy()
            for key, value in cleaned_v.items():
              if value == '':
                cleaned_v[key] = None
            cell.edit(edit_order=edit_order, **cleaned_v) # and update the cell specific values
          else:
            return "Could not create cell %s" % str(cell_index_tuple)
        else:
          return "Cell %s does not exist" % str(cell_index_tuple)

field_prefix_len = len(field_prefix)

def parseField(field):
  """
   Parse given form field, to put them in
   kw or in encapsulated_editor_list
  """
  field_id = field.id
  if field.has_value('alternate_name'):
    field_id = field.get_value('alternate_name') or field_id
  value = getattr(request, field_id, MARKER)
  if hasattr(value, 'edit'):
    # This is an encapsulated editor
    # call it
    encapsulated_editor_list.append(value)
  elif value is not MARKER:
    if field_id.startswith(field_prefix):
      # We only take into account
      # the object attributes
      field_id = field_id[field_prefix_len:]
      # Form: '' -> ERP5: None
      if value == '':
        value = None
      kw[field_id] = value

# Some initilizations
kw = {}
encapsulated_editor_list = []
MARKER = []

# We process all the field in form and
# we check if they are in the request,
# then we edit them
for field in form.get_fields():
  parseField(field)

  ## XXX We need to find a way not to use meta_type.
  field_meta_type = field.meta_type
  if field_meta_type == 'ProxyField':
    field_meta_type = field.getRecursiveTemplateField().meta_type

  if(field_meta_type == 'ListBox'):
    editListBox(field, request.get(field.id))
  elif(field_meta_type == 'MatrixBox'):
    editMatrixBox(field, request.get(field.id))

# Return parsed values
if silent_mode: return (kw, encapsulated_editor_list), 'edit'

# Maybe we should build a list of objects we need
# Update basic attributes
context.edit(REQUEST=request, edit_order=edit_order, **kw)
for encapsulated_editor in encapsulated_editor_list:
  encapsulated_editor.edit(context)

message = request.get('portal_status_message') or Base_translateString("Data updated.")

if message_only:
  return message

ignore_layout = int(ignore_layout)
editable_mode = int(editable_mode)
server_physical_path = context.getPhysicalPath()
server_physical_path = list(server_physical_path)
server_url = request["SERVER_URL"]
server_physical_path.insert(0, server_url)
#calculate direct the url instead of using absolute_url
new_url = '/'.join(server_physical_path)

# for web mode, we should use 'view' instead of passed form_id
# after 'Save & View'.
if context.REQUEST.get('is_web_mode', False) and \
    not editable_mode:
  form_id = 'view'

redirect_url_kw = dict(
    ignore_layout=ignore_layout,
    editable_mode=editable_mode,
    portal_status_message=message
    )
if selection_index:
  redirect_url_kw.update(
    selection_index=selection_index,
    selection_name=selection_name
  )
redirect_url = '%s/%s?%s' % (
    context.absolute_url(),
    form_id,
    make_query(**redirect_url_kw)
    )

result = request['RESPONSE'].redirect(redirect_url)

if silent_mode: return result, 'redirect'
return result
