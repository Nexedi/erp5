"""
 Must call all the script in appropriated order to setup UNG.
"""
from Products.ERP5Type.Log import log
log('Launching activities to setup the demo UNG configuration!')

kw = {}
installed_business_template_list = context.portal_templates.getInstalledBusinessTemplateTitleList()

if 'erp5_web_ung_theme' not in installed_business_template_list:
  kw = context.Alarm_installUngBusinessTemplateList()

context.activate(**kw).Alarm_configureUng()

log('Finished to launch the activities to setup the demo UNG configuration!')
context.setEnabled(False)
