if not context.portal_actions.listFilteredActionsFor(context).has_key('object_print'):
  return None

new_print_action_list = context.Base_fixDialogActions(
     context.Base_filterDuplicateActions(
     context.portal_actions.listFilteredActionsFor(context)), 'object_print')
if new_print_action_list:
  #return new_print_action_list[0]['original_url']
   return new_print_action_list[0]['url']

return None
