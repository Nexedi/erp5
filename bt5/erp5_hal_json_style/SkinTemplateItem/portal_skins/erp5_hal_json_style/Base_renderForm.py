"""Render form while keeping its values back to user.

This script differs from Base_redirect that it keeps the form values in place.

:param message: {str} message to be displayed at the user
:param level: {str|int} severity of the message using ERP5Type.Log levels or their names like 'info', 'warn', 'error'
:param keep_items: {dict} items to be available in the next call. They will be either added as hidden fields to the
                   rendered form or in case of "portal_status_message" just displayed to the user
:param REQUEST: request
:param **kwargs: should contain parameters to ERP5Document_getHateoas such as 'query' to replace Selections
"""
REQUEST = REQUEST or context.REQUEST

form = getattr(context, form_id)

# recover "hidden field" from HAL_JSON interface behind developers back (sorry)
extra_param_json = REQUEST.get('extra_param', {})

if keep_items is not None:
  if not message and "portal_status_message" in keep_items:
    message = keep_items.pop("portal_status_message")

  if not level and "portal_status_level" in keep_items:
    level = keep_items.pop("portal_status_level")

  extra_param_json.update(keep_items)

return context.ERP5Document_getHateoas(form=form, mode='form', REQUEST=REQUEST, extra_param_json=extra_param_json,
                                       portal_status_message=message, portal_status_level=level, **kwargs)
