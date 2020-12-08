# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base
#
# TODO
#   - Implement validation of matrix fields
#   - Implement validation of list fields
#
from Products.Formulator.Errors import FormValidationError
from ZTUtils import make_query

request=context.REQUEST

try:
  # Define form basic fields
  form = getattr(context,form_id)
  edit_order = form.edit_order
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
  # Update listbox attributes
  listbox = request.get('listbox')
  if listbox is not None:
    listbox_field = form.get_field('listbox')
    gv = {}
    if listbox_field.has_value('global_attributes'):
      hidden_attributes = [x[0] for x in listbox_field.get_value('global_attributes')]
      for k in hidden_attributes:
        gv[k] = getattr(request, k,None)
    for property_, v in listbox.items():
      v.update(gv)
      context.setCriterion(property_, **v)
  # Update basic attributes
  context.edit(REQUEST=request, edit_order=edit_order, **kw)
  context.reindexObject()
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)
else:
  # for web mode, we should use 'view' instead of passed form_id
  # after 'Save & View'.
  if context.REQUEST.get('is_web_mode', False) and \
      not editable_mode:
    form_id = 'view'

  if not selection_index:
    redirect_url = '%s/%s?%s' % (
      context.absolute_url(),
      form_id,
      make_query({'ignore_layout':ignore_layout,
                  'editable_mode':editable_mode,
                  'portal_status_message':'Data Updated.',
                  })
      )
  else:
    redirect_url = '%s/%s?%s' % (
      context.absolute_url(),
      form_id,
      make_query({'selection_index':selection_index,
                  'selection_name':selection_name,
                  'ignore_layout':ignore_layout,
                  'editable_mode':editable_mode,
                  'portal_status_message':'Data Updated.',
                  })
      )

request[ 'RESPONSE' ].redirect( redirect_url )
