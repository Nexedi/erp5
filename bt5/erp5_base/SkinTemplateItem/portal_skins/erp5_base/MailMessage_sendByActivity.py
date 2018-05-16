
context.getPortalObject().portal_catalog.searchAndActivate(
  method_id="Entity_sendEmail",
  destination_related_uid=context.getUid(),
  method_kw=method_kw,
  activate_kw=kw.pop('activate_kw', {}),
  **kw)
