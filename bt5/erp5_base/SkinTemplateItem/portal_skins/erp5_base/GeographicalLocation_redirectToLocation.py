"""
  Redirect to external map provider.
  In some case we can render an ERP% form and never leave ERP5 site thus this is
  a simple basic implementation
"""
context.REQUEST.RESPONSE.redirect( \
  'https://www.openstreetmap.org/?lat=%s&lon=%s&zoom=17&layers=M' \
    %(context.getLatitude(), context.getLongitude()))
