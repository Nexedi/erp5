"""
  The purpose of the script is to tell if configuration of a site was finished or not.
  It is used from Deployment Tests.
"""
number_of_activities = len(context.portal_activities.getMessageList())

installed_bt5_list = [x.getTitle() for x in context.portal_templates.getInstalledBusinessTemplateList()]
if "erp5_wendelin" in installed_bt5_list and number_of_activities == 0:
  return 1
else:
  return 0
