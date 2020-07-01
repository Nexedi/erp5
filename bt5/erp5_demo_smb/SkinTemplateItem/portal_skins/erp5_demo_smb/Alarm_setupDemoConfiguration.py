from erp5.component.module.Log import log
log('Launching activities to setup the demo configuration!')

kw = {}
installed_business_template_list = context.portal_templates.getInstalledBusinessTemplateTitleList()

if 'erp5_configurator_standard' not in installed_business_template_list:
  kw = context.Alarm_installBusinessTemplateList()

log('Finished to launch the activities to setup the demo configuration!')
context.setEnabled(False)
