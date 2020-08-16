# It should be ran in an alarm thank to a property sheet constraint.
from ZODB.POSException import ConflictError

if fixit:
  return ["Cannot fix automatically, please do it manually. (Or deactivate the constraint to force upgrade.)"]

portal = context.getPortalObject()

black_list = getattr(context, "Base_getInstalledBusinessTemplateBlackListForModificationList", lambda: ())()
bt_list = [
  x.getObject()
  for x in portal.portal_catalog(
    portal_type="Business Template",
    )
  if x.getInstallationState() == "installed" and x.getTitle() not in black_list and x.getId() not in black_list
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
