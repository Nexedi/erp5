def sortCurrencyCashList(currency_cash_list):
  """Sort a list of currency cash objects
  """
  def sortLines(a_source, b_source):
    """This method helps sorting supported by Python's standard function.
    """
    # Get the currency cash objects. They can be defined as resources.
    if a_source.getPortalType() in ('Coin', 'Banknote'):
      a = a_source
      b = b_source
    else :
      a = a_source.getResourceValue()
      b = b_source.getResourceValue()

    # Second, compare the portal types.
    result = cmp(a.getPortalType(), b.getPortalType())
    if result != 0:
      return result

    # First, compare the base prices (such as 1000 and 2000 Francs CFA).
    result = - cmp(a.getBasePrice(), b.getBasePrice())
    if result != 0:
      return result

    # Last, compare the variations (such as the years 1994 and 2003).
    result = cmp(a.getVariation(), b.getVariation())
    return result

  currency_cash_list.sort(sortLines)
  return currency_cash_list

return sortCurrencyCashList(currency_cash_list)
