"""Render form while keeping its values back to user.

This script differs from Base_redirect that it keeps the form values in place.

:param message: {str} message to be displayed at the user
:param level: {str|int} severity of the message using ERP5Type.Log levels or their names like 'info', 'warn', 'error'
:param keep_items: {dict} items to be available in the next call. They will be either added as hidden fields to the
                   rendered form or in case of "portal_status_message" just displayed to the user
:param REQUEST: request
:param **kwargs: should contain parameters to ERP5Document_getHateoas such as 'query' to replace Selections
"""

keep_items = keep_items or {}

form = getattr(context, form_id)

if not message and "portal_status_message" in keep_items:
  message = keep_items.pop("portal_status_message")

if not level and "portal_status_level" in keep_items:
  level = keep_items.pop("portal_status_level")

return context.ERP5Document_getHateoas(form=form, mode='form', REQUEST=REQUEST, extra_param_json=keep_items,
                                       portal_status_message=message, portal_status_level=level, **kwargs)
