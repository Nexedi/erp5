request = container.REQUEST
kw.update(request.form)

portal = context.getPortalObject()

# Base_updateListboxSelection cannot be found.
Base_updateListboxSelection = getattr(context, 'Base_updateListboxSelection', None)
if Base_updateListboxSelection is not None:
  Base_updateListboxSelection()

action_context = portal.restrictedTraverse(request.get('object_path', '?'), context)

new_print_action_list = context.Base_fixDialogActions(
     context.Base_filterDuplicateActions(
     portal.portal_actions.listFilteredActionsFor(action_context)), 'object_exchange')

if new_print_action_list:
  return context.ERP5Site_redirect(new_print_action_list[0]['url'],
                                                           keep_items={'form_id': form_id,
                                                           'cancel_url': cancel_url,
                                                           'object_path': request.get('object_path', context.getPath()),
                                                           'dialog_category': 'object_exchange'}, **kw)
