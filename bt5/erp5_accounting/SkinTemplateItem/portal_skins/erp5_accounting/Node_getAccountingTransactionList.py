from Products.ERP5Type.Document import newTempBase
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Log import log
portal = context.getPortalObject()
request = portal.REQUEST
params = portal.ERP5Site_getAccountingSelectionParameterDict(selection_name=selection_name)

if params.get('precision', None) is not None:
  # listbox editable float fields uses request/precision to format the value.
  request.set('precision', params['precision'])

if not request.get('is_accounting_report'):
  # if we are in the UI, we use from date from preferences, but in a report we
  # don't use any information from preferences, as they are passed by the
  # report dialog
  from_date = portal.portal_preferences.getPreferredAccountingTransactionFromDate()

# this script can be used for Node, Section or Payment
if kw.get('node_uid'):
  params['node_uid'] = kw['node_uid']
if kw.get('mirror_section_uid'):
  params['mirror_section_uid'] = kw['mirror_section_uid']

if kw.get('ledger', None):
  params['ledger'] = kw['ledger']

category_uid_list = ('payment_uid', 'project_uid', 'funding_uid', 'function_uid',
  'ledger_uid', 'payment_request_uid', 'default_aggregate_uid')
for category_uid in category_uid_list:
  category_uid_value = kw.get(category_uid)
  if category_uid_value:
    if category_uid_value == 'None':
      # XXX Jerome: this code needs some clarification. It is used after a dialog
      # with a list field for project (same for function, payment_request,
      # funding) where the user can select an empty item which means no filter
      # on project, can select a project which means only transactions for
      # that specific project, or select a special value "None" which means
      # transactions that are not related to a project. For that we need a
      # query that will be translated as stock.project_uid IS NULL.      
      params[category_uid] = SimpleQuery(**{category_uid: None})
    else:
      params[category_uid] = category_uid_value

funding_category = kw.get('funding_category')
if funding_category:
  if funding_category == 'None':
    params['funding_uid'] = SimpleQuery(funding_uid=None)
  else:
    params['funding_category'] = funding_category
function_category = kw.get('function_category')
if function_category:
  if function_category == 'None':
    params['function_uid'] = SimpleQuery(function_uid=None)
  else:
    params['function_category'] = function_category

if node_category_strict_membership:
  params['node_category_strict_membership'] = node_category_strict_membership
if node_category:
  params['node_category'] = node_category
if mirror_section_category:
  params['mirror_section_category'] = mirror_section_category

if not 'parent_portal_type' in params:
  params.setdefault('portal_type', portal.getPortalAccountingMovementTypeList())

# Create the related accouting line list
new_result  = []
net_balance = 0.0

# accounts from PL have a balance calculated differently
is_pl_account = False
if params.get('node_uid'):
  if context.getUid() == params['node_uid']: # shortcut
    node = context
  else:
    node, = portal.portal_catalog(uid=params['node_uid'], limit=2)
    node = node.getObject()
  is_pl_account = node.isMemberOf('account_type/expense')\
               or node.isMemberOf('account_type/income')

# remove unknown catalog keys from params
params.pop('detailed_from_date_summary', None)

period_start_date = params.pop('period_start_date', None)
if is_pl_account and not from_date:
  from_date = period_start_date

if portal.portal_selections.getSelectionParamsFor(selection_name).get('omit_grouping_reference'):
  if params.get('at_date'):
    params['grouping_query'] = portal.ERP5Site_getNotGroupedAtDateSQLQuery(params['at_date'])
  else:
    params['grouping_reference'] = None

if from_date or is_pl_account:
  # Create a new parameter list to get the previous balance
  get_inventory_kw = params.copy()

  initial_balance_from_date = from_date

  # ignore any at_date that could lay in params
  get_inventory_kw.pop('at_date', None)

  if period_start_date:
    if is_pl_account:
      # if we have on an expense / income account, only take into account
      # movements from the current period.
      if initial_balance_from_date:
        initial_balance_from_date = max(period_start_date,
                                        initial_balance_from_date)
      else:
        initial_balance_from_date = period_start_date
    else:
      # for all other accounts, we calculate initial balance
      if not initial_balance_from_date:
        # I don't think this should happen
        log('from_date not passed, defaulting to period_start_date')
        initial_balance_from_date = period_start_date

  # Get previous debit and credit
  if not (initial_balance_from_date == period_start_date and is_pl_account):
    getInventoryAssetPrice = portal.portal_simulation.getInventoryAssetPrice
    section_uid_list = params.get('section_uid', [])
    if not same_type(section_uid_list, []):
      section_uid_list = [section_uid_list]
    for section_uid in section_uid_list:
      # We add one initial balance line per section. The main reason is to be able
      # to know the section_title for the GL export.
      # XXX we may also want detail by resource or analytic columns sometimes.
      get_inventory_kw['section_uid'] = section_uid
      # Initial balance calculation uses the same logic as Trial Balance.
      # first to the balance at the period start date
      if is_pl_account:
        period_openning_balance = 0
      else:
        period_openning_balance = getInventoryAssetPrice(
                                                to_date=min(period_start_date,
                                                            initial_balance_from_date),
                                                **get_inventory_kw)

      # then all movements between period_start_date and from_date
      previous_total_debit  = getInventoryAssetPrice(omit_asset_decrease=True,
             from_date=period_start_date,
             to_date=initial_balance_from_date,
             **get_inventory_kw) + max(period_openning_balance, 0)
      previous_total_credit = getInventoryAssetPrice(omit_asset_increase=True,
             from_date=period_start_date,
             to_date=initial_balance_from_date,
             **get_inventory_kw) - max(-period_openning_balance, 0)
  
      if previous_total_credit != 0:
        previous_total_credit = - previous_total_credit
    
      # Show the previous balance if not empty
      if previous_total_credit != 0 or previous_total_debit != 0:
        net_balance = previous_total_debit - previous_total_credit
        previous_balance = newTempBase(portal, '_temp_accounting_transaction')
        previous_balance.edit(
            uid='new_000',
            date=initial_balance_from_date,
            simulation_state_title="",
            credit_price=previous_total_credit,
            debit_price=previous_total_debit,
            total_price=net_balance,
            credit=previous_total_credit,
            debit=previous_total_debit,
            total_quantity=net_balance,
            running_total_price=net_balance,
            is_previous_balance=True,
            Movement_getSpecificReference=u'%s' % translateString('Previous Balance'),
            Movement_getExplanationTitle=u'%s' % translateString('Previous Balance'),
            Movement_getExplanationTranslatedPortalType='',
            Movement_getExplanationReference='',
            Movement_getMirrorSectionTitle='',
            mirror_section_title='',
            Movement_getNodeGapId='',
            getListItemUrl=lambda *args,**kw: None,
            Movement_getExplanationUrl=lambda **kw:None,
            Movement_getFundingTitle=lambda: '',
            Movement_getFunctionTitle=lambda: '',
            Movement_getProjectTitle=lambda: '',
            Node_statAccountingBalance='',
            getTranslatedSimulationStateTitle='',
            modification_date='',
          )

        if context.getPortalType() == 'Account':
          previous_balance.edit(Movement_getExplanationTitle='')
        if params.get('node_uid'):
          previous_balance.edit(
            Movement_getNodeGapId=node.Account_getGapId(),
            node_translated_title=node.getTranslatedTitle(),
            Movement_getNodeFinancialSectionTitle=node.getFinancialSectionTranslatedTitle(),
          )
        if params.get('mirror_section_uid'):
          brain_list = portal.portal_catalog(uid=params['mirror_section_uid'], limit=2)
          if brain_list:
            brain, = brain_list
            previous_balance.edit(
              mirror_section_title=brain.getObject().getTitle()
            )
        # It may happen that user cannot search mirror section from catalog,
        # but our own section should be found.
        section, = portal.portal_catalog(uid=section_uid, limit=2)
        section = section.getObject()
        previous_balance.edit(
          Movement_getSectionPriceCurrency=section.getPriceCurrencyReference(),
          resource_reference=section.getPriceCurrencyReference(),
          section_title=section.getTitle(),
        )
        new_result.append(previous_balance)

  if 'group_by' in kw:
    params['group_by'] = kw['group_by']
  new_result.extend(
    portal.portal_simulation.getMovementHistoryList(
                   from_date=from_date,
                   initial_running_total_price=net_balance,
                   # initial_running_quantity=net_balance, TODO
                   selection_domain=context.portal_selections.getSelectionDomainDictFor(selection_name) or None,
                   sort_on=sort_on,
                   ignore_group_by=True,
                   **params))
  return new_result

# We try not to convert to a list, hence the copy & paste
return portal.portal_simulation.getMovementHistoryList(
                 from_date=from_date,
                 initial_running_total_price=net_balance,
                 # initial_running_quantity=net_balance, TODO
                 selection_domain=context.portal_selections.getSelectionDomainDictFor(selection_name) or None,
                 sort_on=sort_on,
                 ignore_group_by=True,
                 src__=src__,
                 **params)
