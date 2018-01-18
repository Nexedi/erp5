preference = context.portal_preferences.accounting_zuite_preference
preference.edit(
  preferred_account_number_method='account_reference',
  preferred_report_style=report_style)

return "Preference Set"
