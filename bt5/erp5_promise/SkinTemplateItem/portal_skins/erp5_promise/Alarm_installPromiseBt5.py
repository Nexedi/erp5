from Products.ERP5.Tool.TemplateTool import CATALOG_UPDATABLE

portal = context.getPortalObject()
bt5 = portal.getPromiseParameter('portal_templates', 'expected_bt5')

if bt5 is None:
  return

bt5_list = bt5.split()
bt5_list.extend(portal.portal_templates.getInstalledBusinessTemplateTitleList())
portal.portal_templates.upgradeSite(bt5_list, update_catalog=CATALOG_UPDATABLE)
