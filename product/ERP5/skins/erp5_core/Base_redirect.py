## Script (Python) "Base_redirect"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=relative_url=None
##title=
##
# You can use this script to jump to another module / document without making the URL longer.
# Like 'erp5/organisation/purchase_order/accounting/view'.
#
# Usage: .../Base_redirect?relative_url=purchase_order
#
# If you omit the parameter relative_url, this jumps to the portal (i.e. ERP5 Site).

request=context.REQUEST

if relative_url is None:
  redirect_url = '%s/view' % (context.getPortalObject().absolute_url())
else:
  redirect_url = '%s/%s/view' % (context.getPortalObject().absolute_url(), relative_url)

request[ 'RESPONSE' ].redirect( redirect_url )
