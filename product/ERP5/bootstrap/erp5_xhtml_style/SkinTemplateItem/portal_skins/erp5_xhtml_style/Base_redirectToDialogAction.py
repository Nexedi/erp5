# pylint: disable=redefined-builtin
# this script uses format argument
if '?' in dialog_action_url:
  dialog_action_url = '%s&form_id=%s' % (dialog_action_url, form_id)
else:
  dialog_action_url = '%s?form_id=%s' % (dialog_action_url, form_id)


if format:
  # Add format parameter if not null
  dialog_action_url += '&format=%s' % (format,)
return container.REQUEST.RESPONSE.redirect(dialog_action_url)
