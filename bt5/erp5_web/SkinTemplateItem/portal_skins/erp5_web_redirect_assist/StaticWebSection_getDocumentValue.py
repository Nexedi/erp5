"""
================================================================================
Proxy of StaticWebSection_getDocumentValue to allow redirection
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# name                           main_template

# this script will be cloned into a new one. If the request arrives here, it's because it's using the static web section for hateoas URLs
# so name should be the relative_url (e.g. portal_types/Web%20Page/jio_view)
# that relative_url should be use to call ERP5Document_getHateoas script
# with query: ?mode=traverse&relative_url=portal_types%2FWeb%20Page%2Fjio_view&view=definition_view

# catch KeyError on source_path with urls "", "?", "/?", "...&"
try:
  context.REQUEST.other['source_path'] = name
except KeyError:
  return context
return context
