configuration_save = context.restrictedTraverse(configuration_save_url)

gap_info_list = context.BusinessConfiguration_getAvailableGAPList()
selected_gap_info = None
for gap_info in gap_info_list:
  if gap_info['id'] == accounting_plan:
    selected_gap_info = gap_info

assert selected_gap_info is not None

## install accounting bt5 template based on selected accounting plan
configuration_save.addConfigurationItem("Standard BT5 Configurator Item",
                                        bt5_id=selected_gap_info['bt5'])

group_id = context.getGlobalConfigurationAttr('group_id')
if group_id is None:
  # if group_id is not found, use 'group'
  group_id = context.getGlobalConfigurationAttr('group')

accounting_transaction_simulation_state_list = 'delivered stopped' # XXX is it OK not to pass a list ?

gap_account_map = context.BusinessConfiguration_getDefaultAccountList()

for item in gap_account_map[accounting_plan]:
  configuration_save.addConfigurationItem("Account Configurator Item", **item)

## Configure accounting preferences
configuration_save.addConfigurationItem(
          'Preference Configurator Item',
          object_id = 'default_configurator_preference',
          preferred_accounting_transaction_from_date = None,
          preferred_accounting_transaction_at_date = None,
          preferred_section_category = 'group/%s' % group_id,
          preferred_accounting_transaction_section_category = 'group/%s' % group_id,
          preferred_accounting_transaction_gap = selected_gap_info['root'],
          preferred_accounting_transaction_simulation_state_list
                = accounting_transaction_simulation_state_list)

## Configure accounting period
configuration_save.addConfigurationItem("Accounting Period Configurator Item",
                                        start_date=period_start_date,
                                        stop_date=period_stop_date,
                                        short_title=period_title)
