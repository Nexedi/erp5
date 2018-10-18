# This script is used in order to retrieve parameter in the listbox Displayed
# by Base_viewRelatedObjectList from the relation field
result = None

request = context.REQUEST

if parameter is not None:
  field_id = request.get('field_id',None) \
      or request.get('field_your_field_id', None) \
      or request.get('form_id', None)
  form_id = request.get('original_form_id',None) \
      or request.get('field_your_original_form_id', None) \
      or request.get('form_id')
  listbox = getattr(context, form_id).get_field(field_id)
  dialog_id = listbox.get_value('relation_form_id') or 'Base_viewRelatedObjectList'
  result = listbox.get_value(parameter)

  if result in [ [], (), None, '']:
    if parameter == 'proxy_listbox_ids':
      return context.REQUEST.get('proxy_listbox_ids', [])
    if parameter != 'parameter_list':
      result = getattr(context, dialog_id, None).get_field( 'listbox' ).get_orig_value(parameter)

  if parameter == 'portal_type':
    portal_type = listbox.get_value('portal_type')
    proxied_listbox = None
    relation_field_proxy_listbox = context.Base_getRelationFieldProxyListBoxId()
    if relation_field_proxy_listbox != \
            'Base_viewRelatedObjectListBase/listbox':
      proxied_listbox = context.restrictedTraverse(
                relation_field_proxy_listbox, None)
    if proxied_listbox is None:
      return portal_type

    proxied_listbox_portal_type = proxied_listbox.get_value('portal_types')
    portal_type_first_item_list = [x[0] for x in portal_type]
    return [x for x in proxied_listbox_portal_type if x[0] in portal_type_first_item_list] or portal_type

return result
