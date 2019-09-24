context.Zuite_setPreference('')
preference = context.portal_preferences.erp5_ui_test_preference
preference.edit(
  preferred_report_style='ODS',
  preferred_report_format='html',
  preferred_accounting_transaction_section_category='group/demo_group',
  preferred_section_category='group/demo_group',
  preferred_accounting_transaction_source_ection='organisation_module/my_organisation'
)

return 'Set Deferred Preference Successfully.'
