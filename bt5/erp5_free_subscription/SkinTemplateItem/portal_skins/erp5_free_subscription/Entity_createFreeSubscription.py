from Products.ERP5Type.Message import translateString
free_subscription = context.getPortalObject().free_subscription_module.newContent(
  portal_type='Free Subscription',
  destination_value=context,
  source=source,
  resource=resource,
  effective_date=start_date,
  title=title)

free_subscription.validate()

if batch_mode:
  return free_subscription

return context.Base_redirect(form_id, keep_items=dict(
  portal_status_message=translateString("New free subscription created")))
