# pylint:disable=redefined-builtin
portal = context.getPortalObject()
assert alarm_relative_url
alarm = portal.restrictedTraverse(alarm_relative_url)
assert callback_script_id
callback = getattr(alarm, callback_script_id)
callback(
    subject=subject,
    attachment_list=attachment_list,
    **callback_script_kwargs
)
