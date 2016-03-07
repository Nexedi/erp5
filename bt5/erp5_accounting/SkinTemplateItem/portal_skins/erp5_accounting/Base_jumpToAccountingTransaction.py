# Usage: .../Base_jumpToAccountingTransaction?from_entity=1
#
# Use from_account to display only transaction related to the account you come from, and from_entity if you come from an organisation or person

redirect_kw = dict(reset=1,
                   ignore_hide_rows=True)

if from_account:
  redirect_kw['node'] = [context.getRelativeUrl()]
elif from_entity:
  redirect_kw['entity'] = context.getRelativeUrl()

return context.getPortalObject().accounting_module.Base_redirect(
              'view', keep_items=redirect_kw)
