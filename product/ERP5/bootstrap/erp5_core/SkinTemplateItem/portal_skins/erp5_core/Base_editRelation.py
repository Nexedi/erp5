# Updates relation of an ERP5 document
from Products.ERP5Form.MultiRelationField import SUB_FIELD_ID

if listbox_uid is not None:
  selection_tool = context.getPortalObject().portal_selections
  selection_tool.updateSelectionCheckedUidList(
              selection_name, listbox_uid, uids)
  uids = selection_tool.getSelectionCheckedUidsFor(selection_name)

old_request = dict(saved_form_data)

field = getattr(context, form_id).get_field(field_id)
field_key = field.generate_field_key()
if old_request.has_key('sub_index'):
  if len(uids) > 0:
    # XXX Hardcoded
    sub_field_key = field.generate_subfield_key("%s_%s" % (SUB_FIELD_ID, old_request['sub_index']), key=field_key)
    old_request[sub_field_key] = str(uids[0])
else:
  # XXX Not very dynamic...
  sub_field_key = field.generate_subfield_key(SUB_FIELD_ID, key=field_key)
  old_request[sub_field_key] = uids
  old_request[field_key] = uids

request = container.REQUEST
request_form = request.form
for k in request_form.keys():
  del request_form[k]

request.form.update(old_request)
edit_method = getattr(context, request_form.get('form_action', 'Base_edit'))
return edit_method(form_id,
                   ignore_layout=request.get('ignore_layout', True),
                   selection_index=old_request.get('selection_index', 0),
                   selection_name=old_request.get('selection_name', ''))
