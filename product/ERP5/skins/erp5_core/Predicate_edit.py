## Script (Python) "Predicate_edit"
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
  # Update listbox attributes
  listbox = request.get('listbox')
  if listbox is not None:
    listbox_field = form.get_field('listbox')
    gv = {}
    if listbox_field.has_value('global_attributes'):
      hidden_attributes = map(lambda x:x[0], listbox_field.get_value('global_attributes'))
      for k in hidden_attributes:
        gv[k] = getattr(request, k,None)
    for property, v in listbox.items():
      v.update(gv)
      context.setCriterion(property, **v)
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
