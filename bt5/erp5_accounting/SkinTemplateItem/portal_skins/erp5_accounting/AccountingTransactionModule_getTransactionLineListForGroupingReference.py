from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, NegatedQuery, ComplexQuery

request = container.REQUEST
portal = context.getPortalObject()

# we use a different selection for dialog params, because we never want this
# selection to be reseteted
dialog_selection_params = portal.portal_selections.getSelectionParamsFor(
                               'grouping_reference_fast_input_selection')

# support pseudo sorting; sorting is done by uid.
sort_on = []
for column in portal.portal_selections.getSelectionSortOrder(
                 'accounting_transaction_module_grouping_reference_fast_input'
                 ) or (('date', 'ascending'),):
  # column can be couple or a triplet
  column_id = column[0]
  if column_id in ('grouping_reference', 'date', 'parent_title'):
    sort_on.append(column)
  else:
    if column_id == 'node_title':
      column_id = 'stock.node_uid'
    elif column_id == 'Movement_getMirrorSectionTitle':
      column_id = 'stock.mirror_section_uid'
    else:
      continue
    sort_on.append((column_id, column[1]))

section_category = kw.get(
  'section_category',
  portal.portal_preferences.getPreferredAccountingTransactionSectionCategory())
section_category_strict = kw.get(
  'section_category_strict',
  portal.portal_preferences.getPreferredAccountingSectionCategoryStrict())

section_uid = portal.Base_getSectionUidListForSectionCategory(
     section_category, section_category_strict)

currency = portal.Base_getCurrencyForSectionCategory(section_category, section_category_strict)
precision = portal.account_module.getQuantityPrecisionFromResource(currency)
request.set('precision', precision)

grouping = dialog_selection_params.get('grouping', 'grouping')

search_kw = dict(
  portal_type=portal.getPortalAccountingMovementTypeList(),
  node_uid=-1 # prevent a query for all nodes, it would retrieve too many rows.
)
node = node or request.get('node') or dialog_selection_params.get('node')
if node:
  search_kw['node_uid'] = portal.restrictedTraverse(node).getUid()
mirror_section = mirror_section or request.get('mirror_section')
if mirror_section:
  search_kw['mirror_section_uid'] = portal.restrictedTraverse(
                                          mirror_section).getUid()
ledger = ledger or request.get('ledger')
if ledger:
  search_kw['ledger_uid'] = [
    portal.portal_categories.restrictedTraverse(x).getUid() for x in ledger]

if grouping == 'grouping':
  search_kw['grouping_reference'] = None
else:
  assert grouping == 'ungrouping', grouping
  search_kw['grouping_reference'] = NegatedQuery(SimpleQuery(grouping_reference=None))

if title:
  search_kw['title_query'] = ComplexQuery(SimpleQuery(title=title),
                                          SimpleQuery(parent_title=title),
                                          logical_operator='OR')
if delivery_reference:
  search_kw['parent_reference'] = delivery_reference
if debit_price:
  search_kw['stock.total_price'] = debit_price
if credit_price:
  try:
    search_kw['stock.total_price'] = - float(credit_price['query'])
  except ValueError:
    # happens when user entered a complex query (like "> 100 AND < 200")
    # in that case, there is not much we can do.
    search_kw['stock.total_price'] = credit_price['query']
if date:
  search_kw['stock.date'] = date


return portal.portal_simulation.getMovementHistoryList(
                          section_uid=section_uid,
                          simulation_state=['stopped', 'delivered'],
                          sort_on=sort_on,
                          **search_kw)
