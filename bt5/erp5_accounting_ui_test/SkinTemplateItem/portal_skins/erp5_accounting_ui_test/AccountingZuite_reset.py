portal = context.getPortalObject()
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

# validate rules
for rule in portal.portal_rules.objectValues():
  if rule.getValidationState() != 'validated':
    rule.validate()

# open all accounts, and clear cache if we have validated some new accounts
validated = False
for account in portal.account_module.objectValues():
  if account.getValidationState() != 'validated':
    account.validate()
    validated = True

if validated:
  portal.portal_caches.clearCache(cache_factory_list=('erp5_content_long', ))


# validate third parties and set them a dummy region, because it's required
for entity in ( portal.organisation_module.objectValues() +
                portal.person_module.objectValues() ):
  if entity.getValidationState() != 'validated':
    entity.setRegion('region')
    entity.validate()

# create accounting periods ?
# XXX

# enable preference
ptool = portal.portal_preferences
pref = ptool.accounting_zuite_preference
if pref.owner_info()['id'] != context.REQUEST.AUTHENTICATED_USER.getId():
  # we have to 'own' the preference for the test
  ptool = portal.portal_preferences
  # pref.setId('old_accounting_zuite_preference')
  cb = ptool.manage_copyObjects(['accounting_zuite_preference'])
  pasted, = ptool.manage_pasteObjects(cb)
  pref = ptool[pasted['new_id']]
  
pref.edit(preferred_accounting_transaction_at_date=None)
pref.edit(preferred_accounting_transaction_from_date=None)
pref.edit(preferred_account_number_method=None)
if pref.getPreferenceState() == 'disabled':
  pref.enable()

# reset selections
for form in context.getPortalObject().portal_skins\
                    .erp5_accounting.objectValues(spec=('ERP5 Form',)):
  listbox = getattr(form, 'listbox', None)
  if listbox is not None:
    portal.portal_selections.setSelectionFor(listbox.get_value('selection_name'), None)
# also reset common selections
portal.portal_selections.setSelectionFor('person_selection', None)
portal.portal_selections.setSelectionFor('organisation_selection', None)
portal.portal_selections.setSelectionFor('grouping_reference_fast_input_selection', None)
portal.portal_selections.setSelectionFor('accounting_transaction_module_grouping_reference_fast_input', None)
portal.portal_selections.setSelectionFor('entity_transaction_selection', None)
portal.portal_selections.setSelectionFor('account_module_selection', None)

# set sort order on accounting module
portal.portal_selections.setSelectionParamsFor('accounting_selection', {}) # (this recreates selection)
portal.portal_selections.setSelectionSortOrder('accounting_selection', sort_on=(('operation_date', 'ascending'),))

# set sort order and columns on account module
portal.portal_selections.setSelectionParamsFor('account_module_selection', {}) # (this recreates selection)
portal.portal_selections.setSelectionSortOrder('account_module_selection', sort_on=(('preferred_gap_id', 'ascending'),))
portal.portal_selections.setSelectionColumns('account_module_selection',
    [('preferred_gap_id', 'GAP Number'),
     ('translated_title', 'Account Name'),
     ('translated_validation_state_title', 'State'),
     ('AccountModule_getAccountingTransactionCount', 'Count'),
     ('debit', 'Debit'),
     ('credit', 'Credit'),
     ('debit_balance', 'Debit Balance'),
     ('credit_balance', 'Credit Balance')])

# delete the "dummy account" we create in test_account_gap_parallel_list_field
dummy_account_list = portal.account_module.searchFolder(
  title=SimpleQuery(title='Dummy Account for UI Test', comparison_operator='='))
if dummy_account_list:
  portal.account_module.manage_delObjects([dummy_account_list[0].getId()])

return "Reset Successfully."
