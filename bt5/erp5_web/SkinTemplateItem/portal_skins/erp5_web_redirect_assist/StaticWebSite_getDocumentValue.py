"""
================================================================================
Proxy of StaticWebSection_getDocumentValue to allow redirection
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# name                           main_template

# context.REQUEST.other['actual_url'] = context.REQUEST['ACTUAL_URL']

# catch KeyError on source_path with urls "", "?", "/?", "...&"
try:
  context.REQUEST.other['source_path'] = name
except KeyError:
  return context
return context
