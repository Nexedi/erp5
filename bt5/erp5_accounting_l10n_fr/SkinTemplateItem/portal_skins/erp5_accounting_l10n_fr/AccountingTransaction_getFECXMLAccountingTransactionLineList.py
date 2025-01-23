line_list = []

for line in context.contentValues(
    portal_type=context.getPortalAccountingMovementTypeList()):
  has_amount = True
  if side == 'source':
    account = line.getSourceValue(portal_type='Account')
    if test_compta_demat_compatibility:
      has_amount = bool(
        line.getSourceTotalAssetPrice()
        if line.hasSourceTotalAssetPrice() else line.getQuantity())
  else:
    assert side == 'destination'
    account = line.getDestinationValue(portal_type='Account')
    if test_compta_demat_compatibility:
      has_amount = bool(
        line.getDestinationTotalAssetPrice()
        if line.hasDestinationTotalAssetPrice() else line.getQuantity())

  if account is not None and has_amount:
    line_list.append(line)

return line_list
