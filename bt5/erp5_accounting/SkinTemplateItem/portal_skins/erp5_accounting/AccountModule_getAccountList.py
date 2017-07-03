# precision for editable fields
params = context.ERP5Site_getAccountingSelectionParameterDict(selection_name)
if params.get('precision', None) is not None:
  context.REQUEST.set('precision', params['precision'])

use_account_reference = \
 context.portal_preferences.getPreferredAccountNumberMethod() == 'account_reference'

if preferred_gap_id:
  if use_account_reference:
    kwd['reference'] = preferred_gap_id
  else:
    kwd['preferred_gap_id'] = preferred_gap_id


# XXX workaround for #458, we rewrite sort_on id to sort_on using
# strict_membership.
new_sort_on = []
if sort_on is not None:
  for sort_on_item in sort_on:
    if sort_on_item[0] == 'preferred_gap_id':
      if use_account_reference:
        new_sort_on.append(('reference', sort_on_item[1]))
      else:
        new_sort_on.append(
            ('preferred_gap_strict_membership_id', sort_on_item[1]))
    else:
      new_sort_on.append(sort_on_item)

return context.portal_catalog(sort_on=new_sort_on, **kwd)
