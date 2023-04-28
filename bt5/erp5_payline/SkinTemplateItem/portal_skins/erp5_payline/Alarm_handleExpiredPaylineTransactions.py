tag = script.id
portal = context.getPortalObject()
countMessage = portal.portal_activities.countMessage
now = DateTime()
for payline_transaction in portal.payline_transaction_module.searchFolder(
      simulation_state=('confirmed', 'started'),
      portal_type='Payline Transaction',
# TODO: enable and replace python checking when expiration_date is present in catalog table
#      expiration_date=DateTime().strftime('<"%Y/%m/%d %H:%M:%S"'),
    ):
  if countMessage(tag=tag, path=payline_transaction.path) == 0 and now > payline_transaction.getExpirationDate():
    payline_transaction.activate(activity='SQLDict', tag=tag).PaylineTransaction_inquiry(http_exchange_value=None)
