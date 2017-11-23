from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

assert account_type in ('account_type/asset/receivable', 'account_type/liability/payable')

currency = context.Base_getCurrencyForSection(section_category)
precision = context.account_module.getQuantityPrecisionFromResource(currency)
# we set the precision in request, for formatting on editable fields
portal.REQUEST.set('precision', precision)

section_uid = portal.Base_getSectionUidListForSectionCategory(
  section_category, section_category_strict)

grouping_query = ComplexQuery(
      SimpleQuery(grouping_reference=None),
      SimpleQuery(grouping_date=at_date, comparison_operator=">="),
      logical_operator="OR")

account_number_memo = {}
def getAccountNumber(account_url):
  try:
    return account_number_memo[account_url]
  except KeyError:
    account_number_memo[account_url] =\
      portal.restrictedTraverse(account_url).Account_getGapId()
  return account_number_memo[account_url]

section_title_memo = {None: ''}
def getSectionTitle(uid):
  try:
    return section_title_memo[uid]
  except KeyError:
    section_title = ''
    brain_list = portal.portal_catalog(uid=uid, limit=2)
    if brain_list:
      brain, = brain_list
      section_title = brain.getObject().getTranslatedTitle()
    section_title_memo[uid] = section_title
  return section_title_memo[uid]

last_period_id = 'period_%s' % len(period_list)
line_list = []

extra_kw = {}

ledger = kw.get('ledger', None)
if ledger:
  if not isinstance(ledger, list):
    # Allows the generation of reports on different ledgers as the same time
    ledger = [ledger]
  portal_categories = portal.portal_categories
  ledger_value_list = [portal_categories.restrictedTraverse(ledger_category, None)
                       for ledger_category in ledger]
  for ledger_value in ledger_value_list:
    extra_kw.setdefault('ledger_uid', []).append(ledger_value.getUid())

for brain in portal.portal_simulation.getMovementHistoryList(
                                at_date=at_date,
                                simulation_state=simulation_state,
                                node_category_strict_membership=account_type,
                                portal_type=portal.getPortalAccountingMovementTypeList(),
                                section_uid=section_uid,
                                grouping_query=grouping_query,
                                sort_on=(('stock.mirror_section_uid', 'ASC'),
                                         ('stock.date', 'ASC'),
                                         ('stock.uid', 'ASC')),
                                **extra_kw):
  movement = brain.getObject()
  transaction = movement.getParentValue()

  total_price = brain.total_price or 0
  if account_type == 'account_type/liability/payable':
    total_price = - total_price
  
  line = Object(uid='new_',
                mirror_section_title=getSectionTitle(brain.mirror_section_uid),
                mirror_section_uid=brain.mirror_section_uid,
                total_price=total_price,)

  if detail:
    # Detailed version of the aged balance report needs to get properties from
    # the movement or transactions, but summary does not. This conditional is
    # here so that we do not load objects when running in summary mode.
    line['explanation_title'] = movement.hasTitle() and movement.getTitle() or transaction.getTitle()
    line['reference'] = transaction.getReference()
    line['portal_type'] = transaction.getTranslatedPortalType()
    line['date'] = brain.date
    if brain.mirror_section_uid == movement.getSourceSectionUid() and brain.mirror_node_uid == movement.getSourceUid():
      line['specific_reference'] = transaction.getDestinationReference()
      line['gap_id'] = getAccountNumber(movement.getDestination())
    else:
      line['specific_reference'] = transaction.getSourceReference()
      line['gap_id'] = getAccountNumber(movement.getSource())
      assert brain.mirror_section_uid == movement.getDestinationSectionUid()

  # Note that we use date_utc because date would load the object and we are just
  # interested in the difference of days.
  age = int(at_date - brain.date_utc)
  line['age'] = age
  if age < 0:
    line['period_future'] = total_price
  elif age <= period_list[0]:
    line['period_0'] = total_price
  else:
    for idx, period in enumerate(period_list):
      if age <= period:
        line['period_%s' % idx] = total_price
        break
    else:
      line[last_period_id] = total_price

  line_list.append(line)

return sorted(
  line_list,
  key=lambda x:(x['mirror_section_title'],
                x['mirror_section_uid'], # in case we have two mirror section with same title
                                         # we need lines from same section to be grouped together
                                         # for summary report.
                x.get('date'),
                x.get('explanation_title'),))
