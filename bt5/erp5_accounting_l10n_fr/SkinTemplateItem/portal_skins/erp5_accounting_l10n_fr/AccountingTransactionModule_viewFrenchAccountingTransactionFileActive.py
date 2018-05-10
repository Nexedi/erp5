portal = context.getPortalObject()
at_date = at_date.latestTime()

section_uid_list = portal.Base_getSectionUidListForSectionCategory(
  section_category, section_category_strict)

if from_date is None:
  from_date = portal.Base_getAccountingPeriodStartDateForSectionCategory(
    section_category, at_date)

ledger_obj_list = []
if ledger is not None:
  if not (isinstance(ledger, list) or isinstance(ledger, tuple)):
    ledger = (ledger,)
  category_tool = portal.portal_categories
  for item in ledger:
    ledger_obj_list.append(category_tool.ledger.restrictedTraverse(item))
elif group_by in ('ledger', 'portal_type_ledger'):
  raise ValueError("At least one Ledger is needed for group_by=%r" % group_by)

if search_kw is None:
  search_kw = {}

def _groupedJournalTupleDict():
  portal_type_list = portal.getPortalAccountingTransactionTypeList()

  search_kw['simulation_state'] = simulation_state
  search_kw['accounting_transaction.section_uid'] = section_uid_list
  search_kw['operation_date'] = {'query': (from_date, at_date), 'range': 'minngt' }

  journal_tuple_list = []
  if group_by == 'ledger':
    search_kw['portal_type'] = portal_type_list
    for ledger_obj in ledger_obj_list:
      journal_code = journal_lib = ledger_obj.getReference(ledger_obj.getId())

      ledger_search_kw = search_kw.copy()
      ledger_search_kw['default_ledger_uid'] = ledger_obj.getUid()

      journal_tuple_list.append((journal_code, journal_lib, ledger_search_kw))

  elif group_by == 'portal_type_ledger':
    for ledger_obj in ledger_obj_list:
      for portal_type in portal_type_list:
        portal_type_obj = portal.portal_types[portal_type]
        ledger_reference = ledger_obj.getReference(ledger_obj.getId())
        journal_code = "%s: %s" % (portal_type_obj.getCompactTranslatedTitle(), ledger_reference)
        journal_lib = "%s: %s" % (portal_type_obj.getTranslatedTitle(), ledger_reference)

        portal_type_ledger_search_kw = search_kw.copy()
        portal_type_ledger_search_kw['default_ledger_uid'] = ledger_obj.getUid()
        portal_type_ledger_search_kw['portal_type'] = portal_type

        journal_tuple_list.append((journal_code, journal_lib, portal_type_ledger_search_kw))

  # group_by == 'portal_type' (Default)
  else:
    if ledger_obj_list:
      search_kw['default_ledger_uid'] = [ ledger_obj.getUid() for ledger_obj in ledger_obj_list ]

    for portal_type in portal_type_list:
      portal_type_obj = portal.portal_types[portal_type]
      journal_code = portal_type_obj.getCompactTranslatedTitle()
      journal_lib = portal_type_obj.getTranslatedTitle()

      portal_type_search_kw = search_kw.copy()
      portal_type_search_kw['portal_type'] = portal_type

      journal_tuple_list.append((journal_code, journal_lib, portal_type_search_kw))

  return journal_tuple_list

priority = 4
# Proxy Role needed to create an 'Active Process'
active_process = context.AccountingTransactionModule_createActiveProcessForFrenchAccountingTransactionFile()

if tag is None:
  tag = script.getId()
if aggregate_tag is None:
  aggregate_tag = '%s:aggregate' % tag

for journal_code, journal_lib, journal_search_kw in _groupedJournalTupleDict():
  # This script is executed with Proxy Role, required to create 'Active Process'
  this_journal_active_process = context.AccountingTransactionModule_createActiveProcessForFrenchAccountingTransactionFile()

  portal.portal_catalog.searchAndActivate(
    method_id='AccountingTransaction_postFECResult',
    method_kw=dict(section_uid_list=section_uid_list, active_process=this_journal_active_process.getRelativeUrl()),
    activate_kw=dict(tag=tag, priority=priority),
    **journal_search_kw)

  context.activate(
    tag=aggregate_tag,
    after_tag=tag,
    activity='SQLQueue').AccountingTransactionModule_aggregateFrenchAccountingTransactionFileForOneJournal(
      journal_code,
      journal_lib,
      active_process=active_process.getRelativeUrl(),
      # Proxy Role needed to create an 'Active Process'
      this_journal_active_process=this_journal_active_process.getRelativeUrl())

context.activate(after_tag=(tag, aggregate_tag)).AccountingTransactionModule_aggregateFrenchAccountingTransactionFile(
  at_date,
  active_process.getRelativeUrl(),
  user_name=user_name)
