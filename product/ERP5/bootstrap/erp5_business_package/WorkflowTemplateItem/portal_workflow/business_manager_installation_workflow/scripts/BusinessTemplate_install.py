business_manager = state_change['object']
listbox = state_change.kwargs.get('listbox')
workflow_action = state_change.kwargs.get('workflow_action')

portal_templates = business_manager.getParentValue()
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
  business_manager.install()

# XXX: TODO: Work nedeed on reinstall_action
elif workflow_action == 'reinstall_action':
  business_template.reinstall()
