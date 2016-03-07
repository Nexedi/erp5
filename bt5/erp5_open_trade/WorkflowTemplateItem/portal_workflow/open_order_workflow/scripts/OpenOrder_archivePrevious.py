open_order = sci['object']

if not open_order.getReference():
  return

this_uid = open_order.getUid()

# archive previously active open order with same reference
for open_order in sci.getPortal().portal_catalog.searchResults(
                          portal_type=open_order.getPortalType(),
                          reference=open_order.getReference(),
                          validation_state='validated'):
  if this_uid != open_order.uid:
    open_order.getObject().archive()
