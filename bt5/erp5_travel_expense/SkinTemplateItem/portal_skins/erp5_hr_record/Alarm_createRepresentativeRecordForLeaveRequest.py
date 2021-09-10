from Products.ZSQLCatalog.SQLCatalog import Query
from erp5.component.module.DateUtils import addToDate
from DateTime import DateTime

portal = context.getPortalObject()
portal.portal_catalog.searchAndActivate(
  portal_type="Leave Request",
  method_id='LeaveRequest_createRepresentativeRecord',
  creation_date = Query(creation_date=addToDate(DateTime(), to_add={'day': -90}), range="min"),
  activate_kw={'tag': tag},
)
context.activate(after_tag=tag).getId()
