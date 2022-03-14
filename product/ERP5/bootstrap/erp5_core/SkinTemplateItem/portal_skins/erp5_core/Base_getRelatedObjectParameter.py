# This script is used in order to retrieve parameter in the listbox Displayed
# by Base_viewRelatedObjectList from the relation field

# This dialog can either display a generic listbox (Base_viewRelatedObjectList/listbox)
# that takes its configuration dynamically from the relation field configuration, or
# display listbox from "Proxy Listbox IDs".
# When using a listbox from "Proxy Listbox IDs", that listbox defines the configuration
# and have priority over the relation field configuration.

result = None
request = context.REQUEST

if parameter is not None:
  field_id = request.get('field_id',None) \
      or request.get('field_your_field_id', None) \
      or request.get('form_id', None)
  form_id = request.get('original_form_id',None) \
      or request.get('field_your_original_form_id', None) \
      or request.get('form_id')
  relation_field = getattr(context, form_id).get_field(field_id)
  dialog_id = relation_field.get_value('relation_form_id') or 'Base_viewRelatedObjectList'

  # the listbox from "proxy listbox id"
  proxied_listbox = None
  relation_field_proxy_listbox = context.Base_getRelationFieldProxyListBoxId()
  if relation_field_proxy_listbox != \
          'Base_viewRelatedObjectListBase/listbox':
    proxied_listbox = context.restrictedTraverse(
              relation_field_proxy_listbox, None)

  result = relation_field.get_value(parameter)

  if result in [ [], (), None, '']:
    if parameter == 'proxy_listbox_ids':
      return context.REQUEST.get('proxy_listbox_ids', [])
    if parameter != 'parameter_list':
      result = getattr(context, dialog_id, None).get_field( 'listbox' ).get_orig_value(parameter)

  if parameter == 'parameter_list':
    if proxied_listbox is None:
      return result
    return proxied_listbox.get_value('default_params')

  if parameter == 'portal_type':
    portal_type = relation_field.get_value('portal_type')
    if proxied_listbox is None:
      return portal_type
    proxied_listbox_portal_type = proxied_listbox.get_value('portal_types')
    portal_type_first_item_list = [x[0] for x in portal_type]
    return [x for x in proxied_listbox_portal_type if x[0] in portal_type_first_item_list] or portal_type

return result
