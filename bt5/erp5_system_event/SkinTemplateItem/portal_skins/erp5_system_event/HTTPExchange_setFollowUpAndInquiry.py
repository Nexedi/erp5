assert context.getFollowUp() is None, context.getFollowUp()

http_exchange_resource = context.getPortalObject().portal_categories.http_exchange_resource
resource = context.getResourceValue()
while True:
  codification = resource.getCodification()
  if codification:
    break
  parent = resource.getParentValue()
  if parent == http_exchange_resource:
    raise ValueError('No codification found from %r upward' % (context.getResource(), ))
  assert resource is not parent, context.getResource()
  resource = parent

follow_up = getattr(context, 'HTTPExchange_getFollowUpFor' + codification)()
if follow_up is not None:
  context.setFollowUpValue(follow_up)
  follow_up.getTypeBasedMethod('inquiry')(http_exchange_value=context)
