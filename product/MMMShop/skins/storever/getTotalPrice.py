## Script (Python) "getTotalPrice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Computer Total Price
##
shopping_cart = context.getShoppingCart()
exchange_rate = context.REQUEST['exchange_rate']
cur_code = context.REQUEST['cur_code']
shopmanager = context.getShopManager()[1]
local_fee = shopmanager.send_fee_local
world_fee = shopmanager.send_fee_world
exchange_fee = shopmanager.exchange_fee

all_price = 0
for item in shopping_cart.listProducts():
   product_path = item.getProduct()
   quantity = item.getQuantity()
   variant = item.getVariant()
   product = context.restrictedTraverse(product_path)
   prod_deliver_days = product.delivery_days
   prod_price = product.computePrice(variant)
   price = float(prod_price) / float(exchange_rate)
   total_price = int(quantity) * float(price)
   all_price = float(all_price) + float(total_price)
   item.setDeliveryDays(prod_deliver_days)

if cur_code == shopmanager.local_currency:
   send_fee = float(local_fee)
   exc_fee = float(0)
else:
   send_fee = float(world_fee) / float(exchange_rate)
   exc_fee = float(exchange_fee) / float(exchange_rate)

all_price = float(all_price) + float(send_fee) + float(exc_fee)

return all_price
