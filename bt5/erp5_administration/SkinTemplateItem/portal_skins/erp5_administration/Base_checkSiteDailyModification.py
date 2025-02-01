from DateTime import DateTime
from Products.CMFActivity.ActiveResult import ActiveResult
from Products.ZSQLCatalog.SQLCatalog import Query

portal = context.getPortalObject()
if not check_date:
  check_date = DateTime().earliestTime() - 1

active_process = context.restrictedTraverse(active_process)


for workflow_object in portal.portal_catalog(
  portal_type=(
    'Workflow',
    'Workflow Script',
    'Workflow State',
    'Workflow Transition',
    'Workflow Variable',
    'Worklist',
    'Interaction Workflow'
  ),
  modification_date=Query(modification_date=check_date, range="min"),
  select_list = ['relative_url']
):
  active_process.postResult(ActiveResult(
    severity=100,
    detail='%s is modified' % workflow_object.relative_url))


for sub_path, sub_obj in portal.portal_skins.ZopeFind(portal.portal_skins, search_sub=1):
  modified_date = DateTime(container.last_modified(sub_obj))
  if modified_date >= check_date:
    active_process.postResult(ActiveResult(
      severity=100,
      detail='%s is modified' % sub_path))
