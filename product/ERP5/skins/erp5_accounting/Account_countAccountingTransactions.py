## Script (Python) "Account_countAccountingTransactions"
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


#inventory = context.Resource_zGetInventory(node_uid=context.getUid(), omit_simulation=1,
#                                           resource_uid=(currency.getUid(),),
#                                           simulation_state=('draft', 'planned', 'confirmed', 'stopped', 'delivered'))

inventory = context.Resource_zGetInventory(node_uid=self.uid, omit_simulation=1,
                                           resource_uid=(currency.getUid(),),
                                           simulation_state=('draft', 'planned', 'confirmed', 'stopped', 'delivered'))

inventory = inventory[0]
return str(inventory.stock_uid)
