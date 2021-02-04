# pylint:disable=redefined-builtin
portal = context.getPortalObject()
assert alarm_relative_url
alarm = portal.restrictedTraverse(alarm_relative_url)
report_configuration_script_id = alarm.getProperty('report_configuration_script_id')
assert report_configuration_script_id
config = getattr(alarm, report_configuration_script_id)()[idx]
config['done'](subject, attachment_list)
