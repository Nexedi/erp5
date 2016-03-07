from Products.PythonScripts.standard import Object
portal = context.getPortalObject()
getObject = portal.portal_catalog.getObject
params = portal.ERP5Accounting_getParams(selection_name)

# this also prevents to be called directly
assert 'node_uid' in kw

mirror_section_relative_url = None
if kw.get('mirror_section_uid'):
  mirror_section_relative_url =\
        getObject(kw['mirror_section_uid']).getRelativeUrl()

payment_uid = kw.get('payment_uid', None)

portal_type_filter = 0
if 'parent_portal_type' in params:
  portal_type_filter = 1
  portal_type_list = params['parent_portal_type']

total_debit = 0
total_credit = 0
total_debit_price = 0
total_credit_price = 0

line_list = []
for brain in portal.Base_zGetNotGroupedMovementList(
                                at_date=(from_date - 1).latestTime(), # this is not to_date
                                simulation_state=params['simulation_state'],
                                node_uid=[kw['node_uid']],
                                portal_type=portal.getPortalAccountingMovementTypeList(),
                                section_uid=params['section_uid']):
    
  # manually filter out not interesting lines
  # XXX this is because Base_zGetNotGroupedMovementList is really
  # minimalistic
  if mirror_section_relative_url and \
      brain.mirror_section_relative_url != mirror_section_relative_url:
    continue

  mvt = brain.getObject()
  transaction = mvt.getParentValue()
  
  if portal_type_filter and \
        transaction.getPortalType() not in portal_type_list:
    continue

  is_source = (brain.mirror_section_relative_url == mvt.getDestinationSection())
  if is_source:
    if payment_uid and mvt.getSourcePaymentUid() != payment_uid:
      continue
    if project_uid and mvt.getSourceProjectUid() != project_uid:
      continue
    if function and not (mvt.getSourceFunction() or '').startswith(function):
      continue
    specific_reference = transaction.getSourceReference()
    mirror_section_title = mvt.getDestinationSectionTitle()
    section_title = mvt.getSourceSectionTitle()
  else:
    if payment_uid and mvt.getDestinationPaymentUid() != payment_uid:
      continue
    if project_uid and mvt.getDestinationProjectUid() != project_uid:
      continue
    if function and not (mvt.getDestinationFunction() or '').startswith(function):
      continue
    specific_reference = transaction.getDestinationReference()
    mirror_section_title = mvt.getSourceSectionTitle()
    section_title = mvt.getDestinationSectionTitle()
  

  debit = max(brain.total_quantity, 0)
  total_debit += debit
  credit = max(-brain.total_quantity, 0)
  total_credit += credit

  debit_price = max(brain.total_price, 0)
  total_debit_price += debit_price
  credit_price = max(-brain.total_price, 0)
  total_credit_price += credit_price

  brain_date = brain.date
  if mvt.getStartDate():
    brain_date = brain_date.toZone(mvt.getStartDate().timezone())
  
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
