# It should be ran in an alarm thank to a property sheet constraint.
from ZODB.POSException import ConflictError
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

if fixit:
  return ["Cannot fix automatically, please do it manually. (Or deactivate the constraint to force upgrade.)"]

portal = context.getPortalObject()

bt_title_list, keep_bt_title_list = context.Base_getUpgradeBusinessTemplateList()
keep_bt_title_set = set(keep_bt_title_list)
bt_title_list = [
  title
  for _, title in portal.portal_templates.resolveBusinessTemplateListDependency(bt_title_list)
  if title not in keep_bt_title_set
]

bt_list = [
  bt
  for bt in portal.portal_catalog(
    portal_type="Business Template",
    query=SimpleQuery(title=bt_title_list, comparison_operator='='),
  )
  if bt.getInstallationState() == "installed"
]

diff_list = []
for bt in bt_list:
  try:
    diff = bt.BusinessTemplate_getDiffWithZODBAsText()
    if diff:
      diff_list += ["===== %s =====" % bt.getTitle()] + diff.splitlines()
  except ConflictError:
    raise
  except Exception as e:
    diff_list += ["===== %s =====" % bt.getTitle(), repr(e)]

return diff_list
