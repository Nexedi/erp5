portal = context.getPortalObject()

document_list = portal.portal_catalog(
  limit=limit,
  uid={'query': min_uid, 'range': 'nlt'},
  sort_on=(('uid', 'ASC'),),
)
result_count = len(document_list)

if result_count:
  if result_count == limit:
    portal.portal_activities.activate(activity='SQLQueue', priority=3).ERP5Site_checkDeletedDocumentList(document_list[-1].uid, limit, packet_size)

  column_list = [(x.path, x.uid) for x in document_list]
  for i in range(0, result_count, packet_size):
    portal.portal_activities.activate(activity='SQLQueue').ERP5Site_unindexDeletedDocumentList(column_list[i:i+packet_size])
