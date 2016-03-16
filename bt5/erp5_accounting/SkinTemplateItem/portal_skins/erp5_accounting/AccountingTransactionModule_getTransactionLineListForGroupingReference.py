from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery, ComplexQuery

request = container.REQUEST
portal = context.getPortalObject()
ctool = portal.portal_catalog
stool = portal.portal_simulation

# we use a different selection for dialog params, because we never want this
# selection to be reseteted
dialog_selection_params = portal.portal_selections.getSelectionParamsFor(
                               'grouping_reference_fast_input_selection')

# support pseudo sorting; sorting is done by uid.
orig_sort_on = portal.portal_selections.getSelectionSortOrder(
                 'accounting_transaction_module_grouping_reference_fast_input') or (('date', 'ascending'),)
sort_on = []
for sort_column, sort_order in orig_sort_on:
  if sort_column in ('grouping_reference', 'date', 'parent_title'):
    sort_on += [(sort_column, sort_order)]
  elif sort_column == 'node_title':
    sort_on += [('stock.node_uid', sort_order)]
  elif sort_column == 'Movement_getMirrorSectionTitle':
    sort_on += [('stock.mirror_section_uid', sort_order)]

section_category = portal.portal_preferences.getPreferredAccountingTransactionSectionCategory()
section_category_strict = portal.portal_preferences.getPreferredAccountingSectionCategoryStrict()
section_uid = portal.Base_getSectionUidListForSectionCategory(
     section_category, section_category_strict)

currency = portal.Base_getCurrencyForSectionCategory(section_category, section_category_strict)
precision = portal.account_module.getQuantityPrecisionFromResource(currency)
request.set('precision', precision)

grouping = dialog_selection_params.get('grouping', 'grouping')

search_kw = dict(portal_type=portal.getPortalAccountingMovementTypeList())
node = node or request.get('node') or dialog_selection_params.get('node')
if node:
  search_kw['node_uid'] = portal.restrictedTraverse(node).getUid()
mirror_section = mirror_section or request.get('mirror_section')
if mirror_section:
  search_kw['mirror_section_uid'] = portal.restrictedTraverse(
                                          mirror_section).getUid()

if grouping == 'grouping':
  search_kw['grouping_reference'] = None
else:
  assert grouping == 'ungrouping', grouping
  search_kw['grouping_reference'] = NegatedQuery(Query(grouping_reference=None))

if title:
  search_kw['title_query'] = ComplexQuery(Query(title=title),
                                          Query(parent_title=title),
                                          operator='OR')
if delivery_reference:
  search_kw['parent_reference'] = delivery_reference
if debit_price:
  search_kw['stock.total_price'] = debit_price
if credit_price:
  try:
    search_kw['stock.total_price'] = - float(credit_price['query'])
  except ValueError, e:
    # happens when user entered a complex query (like "> 100 AND < 200")
    # in that case, there is not much we can do.
    search_kw['stock.total_price'] = credit_price['query']
if date:
  search_kw['stock.date'] = date


return stool.getMovementHistoryList(
                          section_uid=section_uid,
                          simulation_state=['stopped', 'delivered'],
                          sort_on=sort_on,
                          **search_kw)
