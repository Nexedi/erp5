# pylint:disable=redefined-builtin
report_configuration_script_id = context.getProperty('report_configuration_script_id')
assert report_configuration_script_id
config = getattr(context, report_configuration_script_id)()[idx]
config['done'](subject, attachment_list)
