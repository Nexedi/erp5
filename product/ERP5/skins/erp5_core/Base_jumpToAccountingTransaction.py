## Script (Python) "Base_jumpToAccountingTransaction"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=from_account=None, from_entity=None
##title=
##
# You can use this script to jump to accounting module without making the URL longer.
# Like 'erp5/organisation/purchase_order/accounting/view'.
#
# Usage: .../Base_jumpToAccountingTransaction?from_entity=1
#
# Use from_account to display only transaction related to the account you come from, and from_entity if you come from an organisation or person

request=context.REQUEST

redirect_url = '%s/accounting/view' % context.getPortalObject().absolute_url()

separator = '?'

if from_account:
  redirect_url += '%snode:list=%s' % (separator, context.getRelativeUrl())
  separator = '&'

elif from_entity:
  redirect_url += '%sentity=%s' % (separator, context.getRelativeUrl())
  separator = '&'

redirect_url += '%sreset=1' % separator

request[ 'RESPONSE' ].redirect( redirect_url )
