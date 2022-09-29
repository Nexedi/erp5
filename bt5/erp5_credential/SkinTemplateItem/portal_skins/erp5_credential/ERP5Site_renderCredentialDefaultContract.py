contract_reference = context.getPortalObject().portal_preferences.getPreferredCredentialContractDocumentReference()
if contract_reference:
  if context.getWebSiteValue():
    result = context.absolute_url() + '/' + contract_reference
  else:
    result = context.WebSection_getDocumentValue(contract_reference)
    if result:
      result = result.getRelativeUrl()
  return '<iframe width="95%%" height="400px" src="%s/asStrippedHTML"></iframe>' % result
