"""
================================================================================
Proxy of StaticWebSection_getDocumentValue to allow redirection
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# name                           main_template

# catch KeyError on source_path with urls "", "?", "/?", "...&"
try:
  context.REQUEST.other['source_path'] = name
except KeyError:
  return context
return context
