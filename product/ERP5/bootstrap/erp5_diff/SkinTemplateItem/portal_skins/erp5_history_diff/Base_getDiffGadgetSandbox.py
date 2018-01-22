# This script returns the sandbox for the gadget displaying
# the ERP5. For the XHTML UI, we use 'public' and for the
# renderJS UI, we use 'iframe'
if context.REQUEST.get('web_site_value', None):
  return 'iframe'
return 'public'
