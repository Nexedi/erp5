# Proxy role Auditor to be able to check document existence in system_event_module

# Note on flood: we mitigate flood effect by generating document id based on
# notification-received data. This means that it is not too complex to get ERP5
# to create many documents if one is able to call notification URL.
# Also, unknown values (notification type, type, ...) are accepted. The should
# probably be rejected instead, once we are confident enough that we do not loose
# important notifications.

form_dict = REQUEST.form
context.log(repr(form_dict))
try:
  notification_type = form_dict['notificationType'].upper()
  object_id = 'payline.' + notification_type + '_' + form_dict[{
    'WEBTRS': 'token',
    'WEBWALLET': 'token',
    'WALLET': 'walletId',
  }[notification_type]]
except KeyError:
  create_activity = True
  object_id = None
  notification_type = None
else:
  form_type = form_dict.get('type')
  if notification_type == 'WALLET' and form_type:
    object_id += '_' + form_type.lower()
  create_activity = object_id not in context.getPortalObject().system_event_module
if create_activity:
  context.activate(
    activity='SQLQueue',
  ).PaylineSOAPConnector_notifyFromPaylineActivity(
    object_id,
    # Provide notificationType separately, so callee does not have to parse request just to store it
    notification_type=notification_type,
    request=context.Base_renderRequestForHTTPExchangeStorage(REQUEST),
  )
# Return a non-empty value, so an HTTP "200 OK" status is generated,
# and not a "204 No Content" as it is interpreted as an error by Payline.
return ' '
