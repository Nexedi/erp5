"""
================================================================================
Lookup a (hardcoded) custom parameter (default image, css-path etc)
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# parameter                    Parameter to lookup
# override_data                Portal Type or relative url passed along

customProxyHandler = getattr(context, "WebPage_getCustomProxyParameter", None)
if customProxyHandler is not None:
  source_data = override_data or context.getUid()
  return customProxyHandler(parameter=parameter, source_data=source_data)
