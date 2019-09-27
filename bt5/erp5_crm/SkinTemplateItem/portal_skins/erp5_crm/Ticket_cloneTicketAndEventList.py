portal = context.getPortalObject()

new_ticket = context.Base_createCloneDocument(form_id=None, batch_mode=True)

portal.portal_catalog.activate(activity='SQLQueue').searchAndActivate(
  portal_type=portal.getPortalEventTypeList(),
  default_follow_up_uid=context.getUid(),
  method_id='Event_clone',
  method_kw=dict(follow_up_relative_url=new_ticket.getRelativeUrl()))

portal_status_message = portal.Base_translateString('Events are beeing cloned in the background.')
keep_items = {'portal_status_message':portal_status_message}
return new_ticket.Base_redirect(form_id=form_id, keep_items=keep_items)
