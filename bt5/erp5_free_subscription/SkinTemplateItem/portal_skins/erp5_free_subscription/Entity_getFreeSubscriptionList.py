kw.update(
  portal_type='Free Subscription',
  default_destination_uid=context.getUid())

return context.getPortalObject().portal_catalog(**kw)
