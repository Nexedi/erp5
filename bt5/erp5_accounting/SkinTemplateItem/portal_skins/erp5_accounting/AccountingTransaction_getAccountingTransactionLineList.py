if not portal_type:
  portal_type = context.getPortalObject().getPortalAccountingMovementTypeList()

sort_dict = {
  'bank': -3,
  'income': 0,
  'expense': -2,
  'receivable': -2,
  'payable': 0,
  'collected_vat': -1,
  'refundable_vat': -1,
}

def getAccountingTransactionLineSortKey(line):
  return sort_dict.get(line.getId(), (line.getIntIndex() or line.getIntId() or 0))

return sorted(context.contentValues(portal_type=portal_type, checked_permission="View"), key=getAccountingTransactionLineSortKey)
