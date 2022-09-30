'''
  return the amount composed by all amount of paysheet line wich category of
  category_list parameter is in variation_category_list of the PaySheet line
  and wich has a base_contribution in the base_contribution_list
'''
if excluded_reference_list is None:
  excluded_reference_list = []

total_price = 0
movement_list = context.getMovementList(portal_type=('Pay Sheet Line', 'Pay Sheet Cell'))
for movement in movement_list:
  # Reference must be checked on line
  if excluded_reference_list:
    if "Cell" in movement.getPortalType():
      line = movement.getParentValue()
    else:
      line = movement
    if line.getReference() in excluded_reference_list:
      continue

  if base_contribution is not None and movement.isMemberOf(base_contribution) or no_base_contribution:

    # base_contribution is mandatory, but not contribution_share. If contribution_share is
    # given, search with it, if not, care only about base_contribution
    if contribution_share is not None and movement.isMemberOf(contribution_share):
      total_price += movement.getTotalPrice()
    elif include_empty_contribution and (contribution_share is None or len(movement.getContributionShareList()) == 0):
      total_price += movement.getTotalPrice()


# Get Precision
precision = context.getPriceCurrencyValue().getQuantityPrecision()

amount = round(total_price, precision)
return amount
