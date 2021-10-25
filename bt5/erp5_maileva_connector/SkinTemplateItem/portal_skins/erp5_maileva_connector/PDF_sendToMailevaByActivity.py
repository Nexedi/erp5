import socket

runtime_environment = context.getActivityRuntimeEnvironment()
if runtime_environment:
  runtime_environment.edit(
    conflict_retry=False,
    max_retry=0)


connector = context.restrictedTraverse(connector)
sender = context.restrictedTraverse(sender)
recipient = context.restrictedTraverse(recipient)

try:
  request, response = connector.submitRequest(recipient, sender, context)
except socket.error, e:
  if e.errno == socket.errno.ECONNREFUSED:
    if runtime_environment:
      runtime_environment.edit(max_retry=None)
  raise e

########XXXXXXXX should processing response to check if submit success or failed
# response is a xml??
##### just set to failed for now
context.fail()


############

http_event = context.system_event_module.newContent(
  portal_type='Maileva Exchange',
  source_value = sender,
  destination_value = recipient,
  resource_value = connector,
  follow_up_value = context,
  request = request,
  response = response
)

http_event.confirm()
