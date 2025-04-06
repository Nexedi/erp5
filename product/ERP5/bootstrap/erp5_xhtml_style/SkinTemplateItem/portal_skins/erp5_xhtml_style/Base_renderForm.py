"""Render form while keeping its values back to user.

This script differs from Base_redirect that it keeps the form values in place.

:param message: {str} message to be displayed at the user
:param level: {str|int} level of the notification, success or error
:param keep_items: {dict} items to be available in the next call. They will be either added as hidden fields to the
                   rendered form or in case of "portal_status_message" just displayed to the user
:param REQUEST: request
:param **kwargs: is used to pass necessary parameters to overcome backend-held state (aka Selections)
"""

keep_items = keep_items or {}

if message and "portal_status_message" not in keep_items:
  keep_items["portal_status_message"] = message

if level and "portal_status_level" not in keep_items:
  keep_items["portal_status_level"] = level

if REQUEST is None:
  REQUEST = context.REQUEST

for key, value in keep_items.items():
  REQUEST.set(key, value)
  REQUEST.form[key] = value

return getattr(context, form_id)()
