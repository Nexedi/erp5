## Script(Python) "setPersonalDetailsParams"
##parameters=
##title=Set the personal details params for use in the checkout page

shopping_cart = context.getShoppingCart()
pdetails = shopping_cart.getPersonalDetails()

context.REQUEST.set('cust_name', pdetails[0])
context.REQUEST.set('cust_address', pdetails[1])
context.REQUEST.set('cust_zipcode', pdetails[2])
context.REQUEST.set('cust_city', pdetails[3])
context.REQUEST.set('cust_country', pdetails[4])
context.REQUEST.set('cust_phone', pdetails[5])
context.REQUEST.set('cust_email', pdetails[6])
context.REQUEST.set('cust_vat', '')
context.REQUEST.set('cust_organisation', pdetails[7])
