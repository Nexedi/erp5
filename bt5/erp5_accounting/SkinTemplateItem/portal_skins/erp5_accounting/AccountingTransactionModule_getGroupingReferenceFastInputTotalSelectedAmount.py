"""Selected amount in grouping fastinput is set in request by the update scripts,
but this update script will not be called when searching the listbox.

In that case, we can still calculcate.
"""
portal = context.getPortalObject()
selection_name = \
  context.AccountingTransactionModule_viewGroupingFastInputDialog.listbox.get_value('selection_name')

total_selected_amount = 0
# calculate total selected amount
selected_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)
if selected_uid_list:
  for line in portal.portal_catalog(uid=selected_uid_list):
    line = line.getObject()
    if line.AccountingTransaction_isSourceView():
      total_selected_amount += (line.getSourceInventoriatedTotalAssetPrice() or 0)
    else:
      total_selected_amount += (line.getDestinationInventoriatedTotalAssetPrice() or 0)
return total_selected_amount
