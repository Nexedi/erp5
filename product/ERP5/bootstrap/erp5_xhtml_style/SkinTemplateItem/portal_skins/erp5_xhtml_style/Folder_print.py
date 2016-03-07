request = container.REQUEST
kw.update(request.form)

# Base_updateListboxSelection cannot be found.
Base_updateListboxSelection = getattr(context, 'Base_updateListboxSelection', None)
if Base_updateListboxSelection is not None:
  Base_updateListboxSelection()

new_print_action_list = context.Base_fixDialogActions(
     context.Base_filterDuplicateActions(
     context.portal_actions.listFilteredActionsFor(context)), 'object_print')

if new_print_action_list:
  return context.ERP5Site_redirect(new_print_action_list[0]['url'],
    keep_items={'form_id': form_id,
                'cancel_url': cancel_url,
                'dialog_category': 'object_print'}, **kw)
