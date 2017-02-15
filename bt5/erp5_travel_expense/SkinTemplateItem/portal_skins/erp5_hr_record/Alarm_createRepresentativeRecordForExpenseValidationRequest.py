portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type="Expense Validation Request",
  method_id='ExpenseValidationRequest_createRepresentativeRecord',
  activate_kw={'tag': tag},
)
context.activate(after_tag=tag).getId()
