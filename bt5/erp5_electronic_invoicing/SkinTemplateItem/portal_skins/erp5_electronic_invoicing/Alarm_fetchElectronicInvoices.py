connector_portal_type_list = context.ERP5Site_getElectronicInvoiceConnectorType()

portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type=connector_portal_type_list,
  validation_state="validated",
  method_id="ElectronicInvoicingConnector_fetchAllInvoices",
  activate_kw=dict(tag=tag),
)
context.activate(after_tag=tag).getId()
