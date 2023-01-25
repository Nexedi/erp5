portal = context.getPortalObject()

accounting_currency_reference_cache = container.REQUEST.get('%s.cache' % script.id, {})
def getAccountingCurrencyReference(section_relative_url):
  try:
    return accounting_currency_reference_cache[section_relative_url]
  except KeyError:
    reference = ''
    if section_relative_url:
      section = portal.restrictedTraverse(section_relative_url, None)
      if section is not None:
        reference = section.getProperty('price_currency_reference')
    accounting_currency_reference_cache[section_relative_url] = reference
    return reference

return getAccountingCurrencyReference(brain.section_relative_url)
