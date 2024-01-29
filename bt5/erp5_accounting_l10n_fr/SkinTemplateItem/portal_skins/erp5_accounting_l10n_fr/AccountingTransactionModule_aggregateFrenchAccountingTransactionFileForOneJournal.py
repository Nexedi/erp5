import zlib
from Products.CMFActivity.ActiveResult import ActiveResult
portal = context.getPortalObject()
active_process = portal.restrictedTraverse(active_process)
this_journal_active_process = portal.restrictedTraverse(this_journal_active_process)

# XXX we need proxy role for this
result_list = this_journal_active_process.getResultList()

if result_list:
  journal_fragment = context.AccountingTransactionModule_viewJournalAsFECXML(
      journal_code=journal_code,
      journal_lib=journal_lib,
      result_list=result_list)

  active_process.postResult(ActiveResult(detail=zlib.compress(journal_fragment.encode('utf8'))))

# delete no longer needed active process
this_journal_active_process.getParentValue().manage_delObjects(ids=[this_journal_active_process.getId()])
