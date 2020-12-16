# Script to call in action scripts before executig the actual action.
from erp5.component.module.Log import log
log("ERP5Site_prepare is deprecated, "
    "use Base_updateListboxSelection instead")

# Update checked uids
if None not in (selection_name, uids, listbox_uid):
  context.getPortalObject().portal_selections.updateSelectionCheckedUidList(selection_name, uids=uids, listbox_uid=listbox_uid, REQUEST=context.REQUEST)
