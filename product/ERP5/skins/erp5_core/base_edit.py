##parameters=form_id, selection_index=0, selection_name=''

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base
#
# TODO
#   - Implement validation of matrix fields
#   - Implement validation of list fields
#

from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST

try:
  # Define form basic fields
  form = getattr(context,form_id)
  # Validate
  form.validate_all_to_request(request)
  # Basic attributes
  kw = {}
  # Parse attributes
  for f in form.get_fields():
    k = f.id
    v = getattr(request,k,None)
    if v is not None:
      if k[0:3] == 'my_':
        # We only take into account
        # the object attributes
        k = k[3:]
        kw[k] = v
  # Update matrix attributes
  matrixbox = request.get('matrixbox')
  if matrixbox is not None:
    matrixbox_field = form.get_field('matrixbox')
    cell_base_id = matrixbox_field.get_value('cell_base_id')
    kd = {}
    kd['base_id'] = cell_base_id
    gv = {}
    if matrixbox_field.has_value('global_attributes'):
      hidden_attributes = map(lambda x:x[0], matrixbox_field.get_value('global_attributes'))
      for k in hidden_attributes:
        gv[k] = getattr(request, k,None)
    if matrixbox_field.get_value('update_cell_range'):
      # Update cell range each time it is modified
      lines = matrixbox_field.get_value('lines')
      columns = matrixbox_field.get_value('columns')
      tabs = matrixbox_field.get_value('tabs')
      column_ids = map(lambda x: x[0], columns)
      line_ids = map(lambda x: x[0], lines)
      tab_ids = map(lambda x: x[0], tabs)
      # There are 2 cases
      # Case 1: we do 2 dimensional matrices
      # Case 2: we do 2 dimensinal matrices + tabs
      # In Case 1, we set a 2 dimension range
      # In Case 2, we set a 3 dimension range
      # If tab_id is None, we are in Case 1
      cell_range = context.getCellRange(base_id = cell_base_id)
      if len(tab_ids) == 0:
        matrixbox_cell_range = [line_ids, column_ids]
      elif tab_ids[0] == None:
        matrixbox_cell_range = [line_ids, column_ids]
      else:
        matrixbox_cell_range = [line_ids, column_ids, tab_ids]
      if cell_range != matrixbox_cell_range:
        if len(tab_ids) == 0:
          context.setCellRange(line_ids, column_ids, base_id=cell_base_id)
        elif tab_ids[0] == None:
          context.setCellRange(line_ids, column_ids, base_id=cell_base_id)
        else:
          context.setCellRange(line_ids, column_ids, tab_ids, base_id=cell_base_id)
    for k,v in matrixbox.items():
        # Only update cells which still exist
        if context.hasInRange(*k, **kd):
          c = context.newCell(*k, **kd)
          if c is not None:
            c.edit(**gv)  # First update globals which include the def. of property_list
            if v.has_key('variated_property'):
              # For Variated Properties
              value = v['variated_property']
              del v['variated_property']
              if gv.has_key('mapped_value_property_list'):
                # Change the property which is defined by the
                # first element of mapped_value_property_list
                # XXX May require some changes with Sets
                key = gv['mapped_value_property_list'][0]
                v[key] = value
            c.edit(**v) # and update the cell specific values
          else:
            return "Could not create cell %s" % str(k)
        else:
          return "Cell %s does not exist" % str(k)
  # Update listbox attributes
  listbox = request.get('listbox')
  if listbox is not None:
    listbox_field = form.get_field('listbox')
    gv = {}
    if listbox_field.has_value('global_attributes'):
      hidden_attributes = map(lambda x:x[0], listbox_field.get_value('global_attributes'))
      for k in hidden_attributes:
        gv[k] = getattr(request, k,None)
    for url, v in listbox.items():
      o = context.restrictedTraverse(url)
      v.update(gv)
      o.edit(**v)
      o.flushActivity(invoke = 1) # This is required if we wish to provide immediate display
  # Update basic attributes
  context.edit(REQUEST=request,**kw)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)
else:
  if not selection_index:
    redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Data+Updated.'
                              )
  else:
    redirect_url = '%s/%s?selection_index=%s&selection_name=%s&%s' % ( context.absolute_url()
                              , form_id
                              , selection_index
                              , selection_name
                              , 'portal_status_message=Data+Updated.'
                              )



request[ 'RESPONSE' ].redirect( redirect_url )
