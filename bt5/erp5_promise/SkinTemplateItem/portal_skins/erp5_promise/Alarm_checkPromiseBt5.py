from Products.CMFActivity.ActiveResult import ActiveResult
from Products.ERP5.Tool.TemplateTool import BusinessTemplateUnknownError
from Products.ERP5.Tool.TemplateTool import CATALOG_UPDATABLE

portal = context.getPortalObject()
template_tool = portal.portal_templates
bt5 = portal.getPromiseParameter('portal_templates', 'expected_bt5')

if bt5 is None:
  return

active_result = ActiveResult()

bt5_list = bt5.split()
bt5_list.extend(template_tool.getInstalledBusinessTemplateTitleList())

try:
  message_list = template_tool.upgradeSite(bt5_list, dry_run=True,
                                 update_catalog=CATALOG_UPDATABLE)
  severity = len(message_list)
except BusinessTemplateUnknownError as error:
  severity = -1
  detail = str(error)

if severity == -1:
  severity = 5
  summary = "Unable to resolve bt5 dependencies"
elif severity == 0:
  summary = "Nothing to do."
  detail = ""
else:
  summary = "Upgrade needed."
  detail = "Information: %s" % ",".join(message_list)


active_result.edit(
  summary=summary,
  severity=severity,
  detail=detail)

context.newActiveProcess().postResult(active_result)
