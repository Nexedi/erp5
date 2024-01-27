"""Return item list of accounts that can be used as node for this accounting
transaction line.
The id of the line is used to filter the list, unless `omit_filter` is true.
If `mirror` is set to a true value, the list will be filtered for the mirror
node.
"""
from Products.ERP5Type.Cache import CachingMethod
from AccessControl import getSecurityManager

portal = context.getPortalObject()

if omit_filter:
  category_dict = {
    'income': 'account_type',
    'expense': 'account_type',
    'payable': 'account_type',
    'receivable': 'account_type',
    'collected_vat': 'account_type',
    'refundable_vat': 'account_type',
    'bank': 'account_type/asset',
    'cash': 'account_type/asset', }
elif not mirror:
  category_dict = {
    'income': 'account_type/income',
    'expense': 'account_type/expense',
    'payable': 'account_type/liability/payable',
    'receivable': 'account_type/asset/receivable',
    'collected_vat': 'account_type/liability/payable/collected_vat',
    'refundable_vat': 'account_type/asset/receivable/refundable_vat',
    'bank': 'account_type/asset/cash',
    'cash': 'account_type/asset/cash', }
else:
  category_dict = {
    'income': 'account_type/expense',
    'expense': 'account_type/income',
    'payable': 'account_type/asset/receivable',
    'receivable': 'account_type/liability/payable',
    'collected_vat': 'account_type/asset/receivable/refundable_vat',
    'refundable_vat': 'account_type/liability/payable/collected_vat',
    'bank': 'account_type/asset/cash',
    'cash': 'account_type/asset/cash', }

category = category_dict.get(context.getId())

display_cache = {}
display_funct = context.Account_getFormattedTitle

def display(x):
  if x not in display_cache:
    display_cache[x] = display_funct(x)
  return display_cache[x]

def getItemList(category=None, portal_path=None, mirror=0, omit_filter=0,
                simulation_state=None):
  """Returns a list of Account path items. """
  if category is not None:
    cat = portal.portal_categories.resolveCategory(category)
  else:
    cat = portal.portal_categories.account_type
  filter_dict = {}

  # we don't filter in existing transactions or report / search dialogs
  if simulation_state not in ('delivered', 'stopped',
                              'cancelled', 'no_simulation_state'):
    filter_dict['validation_state'] = ('draft', 'validated')

  item_list = cat.getCategoryMemberItemList(
                              portal_type='Account',
                              base=0,
                              display_method=display,
                              sort_key=display,
                              filter=filter_dict)
  return item_list

# wrap the previous method in a cache, including the cache cookie that
# we reset everytime and account is validated or invalidated.
cache_cookie = portal.account_module.getCacheCookie('account_list')
getItemList = CachingMethod(
  getItemList,
  id='AccountingTransactionLine_getNodeItemList-%s-%s-%s' % (
    cache_cookie,
    getSecurityManager().getUser().getIdOrUserName(),
    portal.portal_preferences.getPreferredAccountNumberMethod()),
  cache_factory='erp5_content_long')

# the cache vary with the simulation state of the current transaction,
# to display all accounts when the transaction is already delivered.
simulation_state = 'no_simulation_state'
if hasattr(context, 'getSimulationState'):
  simulation_state = context.getSimulationState()
item_list = getItemList( category=category,
                    portal_path=context.getPortalObject().getPhysicalPath(),
                    mirror=mirror,
                    omit_filter=omit_filter, # XXX possible optim: only one cache if omit_filter
                    simulation_state=simulation_state)

# make sure that the current value is included in this list, this is
# mostly for compatibility with old versions. XXX This is slow.
if omit_filter:
  return item_list

if not hasattr(context, 'getSource'):
  return item_list

for node in (context.getSource(portal_type='Account'),
             context.getDestination(portal_type='Account')):
  if node:
    if node not in [x[1] for x in item_list]:
      return context.AccountingTransactionLine_getNodeItemList(mirror=mirror, omit_filter=1)

return item_list
