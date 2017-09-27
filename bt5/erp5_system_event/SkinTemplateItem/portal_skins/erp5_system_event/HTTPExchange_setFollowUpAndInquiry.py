"""Call HTTPExchange_getFollowUpFor* to find the document to use as follow up
of this HTTP Exchange and call inquiry type-based method on this document.

To use HTTP Exchange framework:
 * you must have created categories in portal_categories/http_exchange_resource
 * your "entry point" script must create an HTTP Exchange using an HTTP Exchange
   Resource as resource category and confirm this HTTP Exchange.
   In this entry point script, you should also set source and destination categories
   if it helps traceability.
   In this entry point script, you should set request and/or response properties.
 * you must create HTTPExchange_getFollowUpFor${HTTP Exchange Resource Codification}
   configuration script that will be called on the context of the HTTP Exchange and
   will be responsible for returning the document on which inquiry will be done.
   This script can create a new document and return it to use as follow up if applicable.
 * you must create a `inquiry` type based method that will be called on this follow up
   document, recieving the HTTP Exchange as argument.

"""
assert not context.hasFollowUp(), context.getFollowUp()

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
