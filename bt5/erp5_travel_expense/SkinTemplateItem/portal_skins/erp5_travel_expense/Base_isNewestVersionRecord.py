doc_id = record_value.getDocId()
portal_type = record_value.portal_type
revision = int(record_value.getRecordRevision())

if not doc_id:
  return False

for brain in context.portal_catalog(portal_type=portal_type, title={'query':doc_id, 'key':'ExactMatch'}):
  if brain.getObject() == record_value:
    continue

  if int(brain.getRecordRevision()) > revision:
    return False
  elif int(brain.getRecordRevision()) == revision:
    if not brain.getSimulationState() in ('cancelled', 'deleted'):
      if int(brain.getId()) <= int(record_value.getId()):
        return False

return True
