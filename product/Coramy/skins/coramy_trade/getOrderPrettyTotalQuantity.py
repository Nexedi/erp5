## Script (Python) "getOrderPrettyTotalQuantity"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
try :
  order = context
  sql_result = order.order_sql_totalizer(order_id=order.getId(),order_type=order.getPortalType())
  result = 'Quantité totale : '+str(sql_result[0].quantity)
except :
  result = 'Quantité totale : '

return result
