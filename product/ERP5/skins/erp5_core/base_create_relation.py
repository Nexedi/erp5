##parameters=form_id, dialog_id, selection_index, selection_name, object_uid, base_category, catalog_index, portal_type, default_module, return_url

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base

sdmlkjsdmlkjfdsdfmlj()
request=context.REQUEST

o = context.portal_catalog.getObject(object_uid)

form = getattr(context,dialog_id)
form.validate_all_to_request(request)
my_field = form.get_fields()[0]
k = my_field.id
values = getattr(request,k,None)
module = context.restrictedTraverse(default_module)

ref_list = []

for v in values:
  if catalog_index == 'id':
    # We should not edit the id field
    # because the object which is created is not attached to a
    # module yet
    id = v
  else:
    id=str(module.generateNewId())
  module.invokeFactory(type_name=portal_type,id=id)
  new_ob = module.get(id)
  kw = {}
  if catalog_index != 'id':
    kw[catalog_index] = v
    new_ob.edit(**kw)
  ref_list.append(new_ob)
  new_ob.flushActivity(invoke=1)

o.setValue(base_category, ref_list, portal_type=[portal_type])

return request[ 'RESPONSE' ].redirect( return_url )


try:
  # Validate the form
  form = getattr(context,form_id)
  form.validate_all_to_request(request)
  my_field = None
  # Find out which field defines the relation
  for f in form.get_fields():
    if f.has_value( 'base_category'):
      if f.get_value('base_category') == base_category:
        k = f.id
        v = getattr(request,k,None)
        if v != context.getProperty(k[3:]):
          my_field = f
  if my_field:
    kw ={}
    kw[my_field.get_value('catalog_index')] = request.get( my_field.id, None)
    context.portal_selections.setSelectionParamsFor('search_relation', kw.copy())
    kw['base_category'] = base_category
    kw['portal_type'] = my_field.get_value('portal_type')
    request.set('base_category', base_category)
    request.set('portal_type', my_field.get_value('portal_type'))
    request.set('form_id', 'search_relation')
    request.set('form_toto', 'search_relation')
    request.set(my_field.get_value('catalog_index'), request.get( my_field.id, None))
    relation_list = context.portal_catalog(**kw)
    if len(relation_list) > 0:
      return context.search_relation( REQUEST=request )
    else:
      request.set('catalog_index', my_field.get_value('catalog_index'))
      request.set('relation_values', request.get( my_field.id, None))
      return context.create_relation_dialog( REQUEST=request )
      pass
      # context.newRelation(base_category, my_field.get_value('portal_type'))
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)
else:
  message = 'Relation+Unchanged.'

if not selection_index:
  redirect_url = '%s/%s?%s' % ( o.absolute_url()
                            , form_id
                            , 'portal_status_message=%s' % message
                            )
else:
  redirect_url = '%s/%s?selection_index=%s&selection_name=%s&%s' % ( o.absolute_url()
                            , form_id
                            , selection_index
                            , selection_name
                            , 'portal_status_message=%s' % message
                            )

request[ 'RESPONSE' ].redirect( redirect_url )
