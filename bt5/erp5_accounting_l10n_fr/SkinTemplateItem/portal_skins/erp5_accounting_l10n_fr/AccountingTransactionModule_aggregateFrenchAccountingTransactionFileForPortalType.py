from Products.CMFActivity.ActiveResult import ActiveResult
portal = context.getPortalObject()
portal_type = portal.portal_types[portal_type]
active_process = portal.restrictedTraverse(active_process)
this_portal_type_active_process = portal.restrictedTraverse(this_portal_type_active_process)

# XXX we need proxy role for this
result_list = this_portal_type_active_process.getResultList()

if result_list:
  journal_fragment = context.AccountingTransactionModule_viewJournalAsFECXML(
      portal_type=portal_type,
      result_list=result_list)
  
  active_process.postResult(ActiveResult(detail=journal_fragment.encode('utf8').encode('zlib')))

# delete no longer needed active process
this_portal_type_active_process.getParentValue().manage_delObjects(ids=[this_portal_type_active_process.getId()])
