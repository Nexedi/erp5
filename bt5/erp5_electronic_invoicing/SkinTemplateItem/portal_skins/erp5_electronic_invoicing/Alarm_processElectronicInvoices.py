portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type="Electronic Invoice",
  validation_state=("awaiting", "confirmed"),
  method_id="ElectronicInvoice_processInvoice",
  activate_kw=dict(tag=tag),
)
context.activate(after_tag=tag).getId()
