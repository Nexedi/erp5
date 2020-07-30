'''
  Manager proxy role to be able to access System Event Module and create event
'''
from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

portal = context.getPortalObject()

if 'archive_document' in archive_kw:
  exchange = portal.restrictedTraverse(archive_kw['archive_document'])
  del archive_kw['archive_document']
else:
  exchange = portal.system_event_module.newContent(
    portal_type='HTTP Exchange',
    activate_kw=archive_kw.get('activate_kw'),
  )

exchange.edit(
  request=raw_request,
  response=raw_response,
  resource_value=getattr(portal.portal_categories.http_exchange_resource.dqe, service),
  comment=comment,
  **archive_kw
)
exchange.confirm()
exchange.acknowledge()
