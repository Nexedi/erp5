## Script (Python) "Account_getTotalSourceCredit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=self
##title=
##
currency = None

if currency in (None, 'None'):
  currency = context.currency.EUR

total = 0.0
try:
  inventory = context.Resource_zGetInventory(node_uid=context.getUid(), omit_output=1, omit_simulation=1,
                                             resource_uid=(currency.getUid(),),
                                             simulation_state=('draft', 'planned', 'confirmed', 'stopped', 'delivered'))
  total = inventory[0].inventory or 0.0
except:
  pass

return '%.02f' % total
