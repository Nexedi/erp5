request=context.REQUEST

form = getattr(context,form_id)
field = form.get_field(field_id)
base_category = field.get_value('base_category')
portal_type = [x[0] for x in field.get_value('portal_type')]
kw = {}
for k, v in field.get_value('parameter_list') :
  kw[k] = v
accessor_name = 'get%sValueList' % ''.join([part.capitalize() for part in base_category.split('_')])
jump_reference_list = getattr(context, accessor_name)(portal_type=portal_type, filter=kw)

if len(jump_reference_list)==1:
  jump_reference = jump_reference_list[0]
  return jump_reference.Base_redirect()
else:
  selection_uid_list = [x.getUid() for x in jump_reference_list] or None
  kw = {'uid': selection_uid_list}
  # We need to reset the selection. Indeed, some sort columns done in another 
  # jump could be meaningless for this particular jump. The consequence could 
  # be an empty list
  context.portal_selections.setSelectionFor('Base_jumpToRelatedObjectList', None)
  context.portal_selections.setSelectionParamsFor('Base_jumpToRelatedObjectList',kw)
  request.set('object_uid', context.getUid())
  request.set('uids', selection_uid_list)
  request.set('original_form_id', form_id)
  return context.Base_jumpToRelatedObjectList(uids=selection_uid_list, REQUEST=request)
