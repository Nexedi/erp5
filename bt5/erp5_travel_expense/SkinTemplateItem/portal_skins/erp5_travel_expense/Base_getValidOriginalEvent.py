if not record_value.getCopyOf():
  return ValueError

original_event = context.getPortalObject().restrictedTraverse(record_value.getCopyOf())

if original_event is None:
  raise ValueError

if not original_event.getSimulationState() in ('cancelled', 'deleted', 'draft', 'error'):
  return original_event

record_list = []
for brain in context.portal_catalog(portal_type=record_value.portal_type, title={'query':record_value.getDocId(), 'key':'ExactMatch'}):
  record = brain.getObject()
  if record in (record_value, original_event):
    continue
  if not record.getSimulationState() in ('cancelled', 'deleted', 'draft'):
    record_list.append(record)

if not record_list:
  return None

record_list.sort(key=lambda x:(x.getRecordRevision(), int(x.getId())))
return record_list[-1]
