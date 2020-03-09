"""
  The purpose of the script is to tell if configuration of a site was finished or not.
  It is used from Deployment Tests.
"""
installed_bt5_list = [x.getTitle() for x in context.portal_templates.getInstalledBusinessTemplateList()]
if "erp5_accounting" in installed_bt5_list:
  return 1
else:
  return 0
