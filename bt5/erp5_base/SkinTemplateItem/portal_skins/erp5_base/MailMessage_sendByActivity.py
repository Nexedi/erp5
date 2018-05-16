# We do not want to retry those activities, as sending email is not transactional safe
activate_kw = kw.pop('activate_kw', {})

context.getPortalObject().portal_catalog.searchAndActivate(
  method_id="Entity_sendEmail",
  destination_related_uid=context.getUid(),
  method_kw=method_kw,
  activate_kw=activate_kw,
  **kw)
