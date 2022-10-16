"""
Called right after a Payline call is made, before response is returned to caller.

Archive exchange's raw data in system_event_module as an HTTP Exchange document.
"""
# TODO: remove manaer proxy role
portal = context.getPortalObject()

def getdoc(document, identifier):
  # For consistency with how suds looks functions up.
  if identifier is None:
    if len(document) > 1:
      raise ValueError(
        'Ambiguous document lookup: %r has more than one child' % (
          document.getPath(),
        )
      )
    return list(document.values())[0]
  return getattr(document, identifier)

exchange = portal.system_event_module.newContent(
  portal_type='HTTP Exchange',
  request=raw_request, # XXX: this is not HTTP, but a SOAP message
  response=raw_response, # XXX: this is not HTTP, but a SOAP message
  # Note: it is important to use an ObjectManager method to retrieve final
  # category (get, __getattr__, __getitem__), as their name may clash with
  # method names (__getattr__) or properties (getProperty, __getattr__).
  # So "get" it is.
  resource_value=getdoc(
    getdoc(
      portal.portal_categories.http_exchange_resource.payline.query,
      service,
    ),
    port,
  ).get(name),
  follow_up_value=archive_kw['follow_up_value'],
)
exchange.confirm()
# This is a call we initiated, value returned is sufficient to finalise this exchange.
exchange.acknowledge()
