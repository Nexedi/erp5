"""
================================================================================
Lookup a (hardcoded) custom parameter (default image, css-path etc)
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# parameter                    Parameter to lookup

customHandler = getattr(context, "WebPage_getCustomParameter", None)
if customHandler is not None:
  return customHandler(parameter=parameter)
