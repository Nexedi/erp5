from Products.ZSQLCatalog.SQLCatalog import Query
from erp5.component.module.DateUtils import addToDate
from DateTime import DateTime

portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type="Expense Validation Request",
  method_id='ExpenseValidationRequest_createRepresentativeRecord',
  creation_date = Query(creation_date=addToDate(DateTime(), to_add={'day': -120}), range="min"),
  activate_kw={'tag': tag},
)
context.activate(after_tag=tag).getId()
