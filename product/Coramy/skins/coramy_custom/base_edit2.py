## Script (Python) "base_edit2"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id, selection_index=0, selection_name=''
##title=
##
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
      cell_range = context.getCellRange(base_id = cell_base_id)
      if cell_range != [line_ids, column_ids,  tab_ids]:
        if len(tab_ids) > 0:
          context.setCellRange(line_ids, column_ids, tab_ids, base_id=cell_base_id)
        else:
          context.setCellRange(line_ids, column_ids, base_id=cell_base_id)
    for k,v in matrixbox.items():
        # Only update cells which still exist
        if context.hasInRange(*k, **kd):
          c = context.newCell(*k, **kd)
          c.edit(**gv) # Make sure global properties are set (ie. mapped_value_property_list for ex.
          if v.has_key('variated_property'):
            # For Variated Properties
            value = v['variated_property']
            del v['variated_property']
            if gv.has_key('mapped_value_property_list'):
              # Change the property which is defined by the
              # first element of mapped_value_property_list
              key = gv['mapped_value_property_list'][0]
              v[key] = value
          c.edit(**v)
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
  # Update basic attributes
  #return kw
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
