## Script (Python) "Base_jumpToRelatedDocument"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id, field_id, selection_index=0, selection_name=''
##title=
##
# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from ZTUtils import make_query

request=context.REQUEST

#return request


#selection = context.portal_selections.getSelectionFor('modele_view')
#context.portal_selections.setSelectionFor('jump_relation',selection)
#return "ok"

form = getattr(context,form_id)
field = form.get_field(field_id)
base_category = field.get_value('base_category')
portal_type = map(lambda x:x[0],field.get_value('portal_type'))
jump_reference_list = context.getAcquiredValueList(base_category, portal_type=portal_type)
if len(jump_reference_list)==1:
  jump_reference = jump_reference_list[0]
  return request[ 'RESPONSE' ].redirect( '%s/view' % jump_reference.absolute_url() )
else:
  selection_uid_list = map(lambda x:x.getUid(),jump_reference_list)
  kw = {'uid': selection_uid_list}
  context.portal_selections.setSelectionParamsFor('Base_jumpToRelatedObjectList',kw)
  request.set('object_uid', context.getUid())
  request.set('uids', selection_uid_list)
  return context.Base_jumpToRelatedObjectList(uids=selection_uid_list, REQUEST=request)
