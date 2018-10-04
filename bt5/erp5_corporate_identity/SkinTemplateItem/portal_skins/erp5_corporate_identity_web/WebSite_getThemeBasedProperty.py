if parameter is not None and proxy is not None:
  proxyHandler = getattr(context, 'Base_getProxyThemeBasedProperty', None)
  prefixHandler = getattr(context, 'Base_getBasicThemeBasedProperty', None)

  if proxyHandler is not None and proxy == True:
    return proxyHandler(
      parameter=parameter,
      source_uid=source_uid,
      is_site=True
    )

  if prefixHandler is not None and proxy == False:
    return prefixHandler(
      parameter=parameter
    )

return "XXX could not retrieve %s" % (parameter or " undefined parameter")
