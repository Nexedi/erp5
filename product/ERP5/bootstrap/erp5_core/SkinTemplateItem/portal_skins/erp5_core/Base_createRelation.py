# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base

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
    id_ = v
  else:
    id_ = str(module.generateNewId())
  module.invokeFactory(type_name=portal_type, id=id_)
  new_ob = module.get(id_)
  kw = {}
  if catalog_index != 'id':
    kw[catalog_index] = v
    new_ob.edit(**kw)
  ref_list.append(new_ob)
  new_ob.flushActivity(invoke=1)

o.setValue(base_category, ref_list, portal_type=[portal_type])

return request[ 'RESPONSE' ].redirect( return_url )
