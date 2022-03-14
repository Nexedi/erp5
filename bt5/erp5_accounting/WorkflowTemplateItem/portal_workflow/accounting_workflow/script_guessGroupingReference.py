portal = sci.getPortal()

# if we allow grouping with different quantities, we cannot group here
# (because the script will group everything)
if portal.portal_preferences.getPreference(
               'preferred_grouping_with_different_quantities', 0):
  return

sci['object'].AccountingTransaction_guessGroupedLines()
