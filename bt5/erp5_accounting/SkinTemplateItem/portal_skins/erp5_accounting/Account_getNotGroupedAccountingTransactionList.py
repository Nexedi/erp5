from Products.PythonScripts.standard import Object
portal = context.getPortalObject()
params = portal.ERP5Site_getAccountingSelectionParameterDict(selection_name)

# this also prevents to be called directly
assert 'node_uid' in kw

total_debit = 0
total_credit = 0
total_debit_price = 0
total_credit_price = 0

at_date = (from_date - 1).latestTime()
inventory_query = {
  'at_date': at_date, # this is not to_date
  'grouping_query': portal.ERP5Site_getNotGroupedAtDateSQLQuery(at_date),
  'simulation_state': params['simulation_state'],
  'node_uid': kw['node_uid'],
  'portal_type': portal.getPortalAccountingMovementTypeList(),
  'section_uid': params['section_uid'],
  'sort_on': (
    ('stock.date', 'ASC'),
    ('stock.uid', 'ASC'),
  )
}

if kw.get('mirror_section_uid'):
  inventory_query['mirror_section_uid'] = kw['mirror_section_uid']
if kw.get('payment_uid'):
  inventory_query['payment_uid'] = kw['payment_uid']
if project_uid:
  inventory_query['project_uid'] = project_uid
if function:
  inventory_query['function_category'] = function
if params.get('ledger', None):
  inventory_query['ledger'] = params.get('ledger')

if 'parent_portal_type' in params:
  portal_type_list = params['parent_portal_type']
  # only apply this filter if not all portal_types where selected,
  # because it is then unnecessary.
  if set(portal_type_list) != set(portal.getPortalAccountingTransactionTypeList()):
    inventory_query['parent_portal_type'] = portal_type_list

line_list = []

for brain in portal.portal_simulation.getMovementHistoryList(**inventory_query):
  mvt = brain.getObject()
  transaction = mvt.getParentValue()

  is_source = (brain.mirror_section_relative_url == mvt.getDestinationSection())
  if is_source:
    specific_reference = transaction.getSourceReference()
    mirror_section_title = mvt.getDestinationSectionTitle()
    section_title = mvt.getSourceSectionTitle()
  else:
    specific_reference = transaction.getDestinationReference()
    mirror_section_title = mvt.getSourceSectionTitle()
    section_title = mvt.getDestinationSectionTitle()

  debit = max(brain.total_quantity, 0)
  total_debit += debit
  credit = max(-brain.total_quantity, 0)
  total_credit += credit

  debit_price = max((brain.total_price or 0), 0)
  total_debit_price += debit_price
  credit_price = max(-(brain.total_price or 0), 0)
  total_credit_price += credit_price

  line = Object(uid='new_000',
                total_price=brain.total_price,
                date=brain.date,
                Movement_getSpecificReference=specific_reference,
                mirror_section_title=mirror_section_title,
                section_title=section_title,
                debit=debit,
                credit=credit,
                debit_price=debit_price,
                credit_price=credit_price,
                Movement_getExplanationTitleAndAnalytics=brain.Movement_getExplanationTitleAndAnalytics(brain))

  line_list.append(line)


context.REQUEST.set(
  'Account_statNotGroupedAccountingTransactionList.total_debit', total_debit)
context.REQUEST.set(
  'Account_statNotGroupedAccountingTransactionList.total_credit', total_credit)
context.REQUEST.set(
  'Account_statNotGroupedAccountingTransactionList.total_debit_price',
  total_debit_price)
context.REQUEST.set(
  'Account_statNotGroupedAccountingTransactionList.total_credit_price',
  total_credit_price)
return line_list
