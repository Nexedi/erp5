listbox = kw.get('listbox', ())
update_catalog = update_translation = 0

bt_id_list = getattr(context.REQUEST, 'bt_list', ())
bt_dict = {}
for item in listbox:
  # backward compatibility
  if not same_type(item['choice'], []):
    item['choice'] = [item['choice']]

  if item['choice']:
    choice = item['choice'][0]
  else:
    choice = "nothing"
  bt_id, object_id = item['listbox_key'].split('|')
  bt_dict.setdefault(bt_id, {})[object_id] = choice

bt_title_list = []
for bt_id in bt_id_list:
  try:
    object_list = bt_dict[bt_id]
  except KeyError:
    object_list = {}
  if bt_id == bt_id_list[-1]:
    update_catalog = kw.get('update_catalog')
    update_translation = kw.get('update_translation')
  bt = context.portal_templates[bt_id]
  bt.install(force=0, object_to_update=object_list, update_catalog=update_catalog,
             update_translation=update_translation)
  bt_title_list.append(bt.getTitle())

REQUEST = container.REQUEST
RESPONSE = REQUEST.RESPONSE

return RESPONSE.redirect("%s/view?portal_status_message=Business+Template+%s+installed" % \
                         (context.absolute_url(), ',+'.join(bt_title_list)))
