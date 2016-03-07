def sortCurrencyCashList(currency_cash_list):
  """Sort a list of currency cash objects
  """
  def sortLines(a, b):
    """This method helps sorting supported by Python's standard function.
    """
    # First, compare the portal types.
    result = cmp(a.resource_portal_type, b.resource_portal_type)
    if result != 0:
      return result

    # Second, compare the base prices (such as 1000 and 2000 Francs CFA).
    result = cmp(a.base_price, b.base_price)
    if result != 0:
      return result

    # Last, compare the variations (such as the years 1994 and 2003).
    result = cmp(a.cash_status_title, b.cash_status_title)
    if result != 0:
      return result

    result = cmp(getattr(a,'date',None),getattr(b,'date',None))
    return result

  currency_cash_list.sort(sortLines)
  return currency_cash_list

returned_value = context.CounterModule_getVaultTransactionList(**kw)
returned_value = sortCurrencyCashList(returned_value)


return returned_value
