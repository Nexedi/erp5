from DateTime import DateTime
from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()
if not check_date:
  check_date = DateTime().earliestTime() - 1

active_process = context.restrictedTraverse(active_process)

for sub_path, sub_obj in portal.portal_skins.ZopeFind(portal.portal_skins, search_sub=1):
  modified_date = DateTime(container.last_modified(sub_obj))
  if modified_date >= check_date:
    active_process.postResult(ActiveResult(
      severity=100,
      detail='%s is modified' % sub_path))
