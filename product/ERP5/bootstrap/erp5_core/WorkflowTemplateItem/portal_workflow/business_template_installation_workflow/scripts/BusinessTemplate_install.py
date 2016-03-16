business_template = state_change['object']
listbox = state_change.kwargs.get('listbox')
update_catalog = state_change.kwargs.get('update_catalog')
update_translation = state_change.kwargs.get('update_translation')
workflow_action = state_change.kwargs.get('workflow_action')

object_to_update = {}
if listbox is not None and len(listbox) > 0:
  for item in listbox:
    if item['choice']:
      # Choice parameter is now selected with a MultiCheckBoxField with only one element
      # Business Template need to get a string and not a list
      object_to_update[item['listbox_key']] = item['choice'][0]
    else:
      object_to_update[item['listbox_key']] = "nothing"

if workflow_action == 'install_action':
  business_template.install(force=0, object_to_update=object_to_update, \
                            update_catalog=update_catalog, update_translation=update_translation)
elif workflow_action == 'reinstall_action':
  business_template.reinstall(force=0, object_to_update=object_to_update, \
                              update_catalog=update_catalog, update_translation=update_translation)
