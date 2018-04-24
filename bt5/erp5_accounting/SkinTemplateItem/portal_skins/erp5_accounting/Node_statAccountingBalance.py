from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
portal = context.getPortalObject()

params = portal.ERP5Site_getAccountingSelectionParameterDict(selection_name=selection_name)
getSelectionDomainDictFor = context.portal_selections.getSelectionDomainDictFor

if asset_price:
  getInventory = portal.portal_simulation.getInventoryAssetPrice
else:
  getInventory = portal.portal_simulation.getInventory

if kw.get('node_uid'):
  params['node_uid'] = kw['node_uid']

if kw.get('mirror_section_uid'):
  params['mirror_section_uid'] = kw['mirror_section_uid']

category_uid_list = ('payment_uid', 'project_uid', 'funding_uid',
  'ledger_uid', 'function_uid', 'payment_request_uid')
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

if kw.get('node_category_strict_membership'):
  params['node_category_strict_membership'] = \
                kw['node_category_strict_membership']
if kw.get('node_category'):
  params['node_category'] = kw['node_category']
if kw.get('mirror_section_category'):
  params['mirror_section_category'] = kw['mirror_section_category']

###
# Get the 'where_expression' parameter
# XXX can be removed ?
if kw.get('where_expression'):
  params['where_expression'] = kw['where_expression']

if not 'parent_portal_type' in params:
  params.setdefault('portal_type', portal.getPortalAccountingMovementTypeList())

# Remove unsupported inventory API parameters
params.pop('detailed_from_date_summary', None)

if kw.get('ledger', None):
  params['ledger'] = kw.get('ledger')

period_start_date = params.pop('period_start_date', None)
if period_start_date and params.get('node_uid'):
  # find the node for this node_uid
  if context.getUid() == params['node_uid']: # I bet it's context
    node = context
  else:
    node, = portal.portal_catalog(uid=params['node_uid'], limit=2)
    node = node.getObject()
  if node.isMemberOf('account_type/expense') or\
        node.isMemberOf('account_type/income'):
    # For expense or income accounts, we only take into account transactions
    # from the beginning of the period, unless a from_date prior to this
    # beginning is passed explicitly.
    # if we are in the regular user interface, we only limit
    if 'from_date' in kw:
      params['from_date'] = min(kw['from_date'], period_start_date)
  elif kw.get('from_date'):
    # for other account, we calculate the initial balance as the "absolute"
    # balance at the beginning of the period, plus debit or credit from this
    # beginning of period to the from_date
    at_date = params.pop('at_date', None)
    period_openning_balance = getInventory(
              selection_domain=getSelectionDomainDictFor(selection_name) or None,
              to_date=period_start_date,
              **params)
    if omit_asset_decrease:
      return getInventory(omit_asset_decrease=1,
           from_date=period_start_date,
           at_date=at_date,
           **params) + max(period_openning_balance, 0)
    elif omit_asset_increase:
      return getInventory(omit_asset_increase=1,
           from_date=period_start_date,
           at_date=at_date,
           **params) - max(-period_openning_balance, 0)
    return getInventory(
           from_date=period_start_date,
           at_date=at_date,
           **params) + period_openning_balance

return getInventory(
              omit_asset_increase=omit_asset_increase,
              omit_asset_decrease=omit_asset_decrease,
              selection_domain=getSelectionDomainDictFor(selection_name) or None,
              **params)
