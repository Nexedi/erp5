# This script returns the gap id for this account according to the current gap
# XXX This script is badly name, as it does not truly return a category ID.
# XXX Instead, the purpose of this script is more to return an account number to display

preference_tool = context.getPortalObject().portal_preferences

number_method = preference_tool.getPreferredAccountNumberMethod()

if number_method == 'account_reference' and not gap_root:
  reference = context.getReference()
  if reference:
    return reference

## elif number_method == 'gap_id':
# GAP id is the default rendering
current_gap = gap_root or preference_tool.getPreferredAccountingTransactionGap() or ''
for gap in context.getGapValueList():
  if current_gap in gap.getPath():
    return gap.getReference() or gap.getId()
return ''
