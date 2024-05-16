from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from Products.PythonScripts.standard import Object
request = container.REQUEST
portal = context.getPortalObject()

line_list = []

extra_kw = {}
if payment:
  extra_kw['payment'] = payment

if group_by:
  extra_kw['group_by'] = group_by
  extra_kw['ignore_group_by'] = True

if project_uid:
  if project_uid == 'None':
    extra_kw['project_uid'] = SimpleQuery(project_uid=None)
  else:
    extra_kw['project_uid'] = project_uid

if ledger_uid:
  extra_kw['ledger_uid'] = ledger_uid

account_title_cache = {}
def getAccountId(node_relative_url):
  if node_relative_url not in account_title_cache:
    title = portal.restrictedTraverse(node_relative_url).Account_getGapId(gap_root=gap_root)
    account_title_cache[node_relative_url] = title
  return account_title_cache[node_relative_url]


node_search_kw = {
  'portal_type': 'Account'
}
if gap_root:
  node_search_kw['gap_uid'] = portal.portal_categories.gap.restrictedTraverse(gap_root).getUid()
node_uid = [b.uid for b in portal.portal_catalog(**node_search_kw)]

displayed_transaction = {}
total_credit = 0
total_debit = 0

for brain in portal.portal_simulation.getMovementHistoryList(
                                from_date=from_date,
                                at_date=at_date,
                                section_uid=section_uid,
                                portal_type=portal.getPortalAccountingMovementTypeList(),
      # note that we pass both portal_type and parent_portal_type because some transactions
      # may contain some non accounting lines that are in stock table (eg. Pay Sheet Lines)
                                parent_portal_type=portal_type,
                                simulation_state=simulation_state,
                                node_uid=node_uid,
                                sort_on=(('stock.date', 'ASC'),
# FIXME: this should actually be sorted on parent_delivery_specific_reference
# a related key which does not exists, and would anyway not be efficient with
# current tables
                                         ('parent_uid', 'descending'),
                                         ('stock.total_price', 'descending')),
                                **extra_kw):

  debit = max(brain.total_price, 0) or 0
  credit = max(-(brain.total_price or 0), 0) or 0

  mvt = brain.getObject()
  if payment_mode and not \
        mvt.getPaymentMode('').startswith(payment_mode):
    continue

  total_debit += debit
  total_credit += credit

  transaction = mvt.getParentValue()
  is_source = 0
  if transaction.getSourceSection():
    is_source = brain.section_relative_url.startswith(
                  transaction.getSourceSection())

  if is_source:
    mirror_section_title = mvt.getDestinationSectionTitle()
  else:
    mirror_section_title = mvt.getSourceSectionTitle()

  if transaction.getUid() not in displayed_transaction:
    displayed_transaction[transaction.getUid()] = 1
    if is_source:
      specific_reference = transaction.getSourceReference()
    else:
      specific_reference = transaction.getDestinationReference()
    displayed_transaction[transaction.getUid()] = 1
    transaction_reference = transaction.getReference()
    title = mvt.hasTitle() and mvt.getTitle() or transaction.getTitle()
    date = brain.date
  else:
    specific_reference = ''
    transaction_reference = ''
    title = mvt.hasTitle() and mvt.getTitle() or ''
    date = None

  line = Object(uid='new_',
                title=title,
                portal_type=transaction.getTranslatedPortalType(),
                specific_reference=specific_reference,
                parent_reference=transaction_reference,
                mirror_section_title=mirror_section_title,
                node_title=getAccountId(brain.node_relative_url),
                date=date,
                debit=debit,
                credit=credit,)
  analytic_info = {}
  for analytic_column, analytic_column_title in analytic_column_list: # pylint: disable=unused-variable
    if analytic_column == 'project':
      analytic_info['project'] = brain.Movement_getProjectTitle()
    elif analytic_column == 'funding':
      analytic_info['funding'] = brain.Movement_getFundingTitle()
    elif analytic_column == 'function':
      analytic_info['function'] = brain.Movement_getFunctionTitle()
    else:
      analytic_info[analytic_column] = mvt.getProperty(analytic_column)

  line.update(analytic_info)
  line_list.append(line)

request.set(
      'AccountingTransactionModule_getJournalSectionLineList.total_debit',
       total_debit)
request.set(
      'AccountingTransactionModule_getJournalSectionLineList.total_credit',
       total_credit)

return line_list
