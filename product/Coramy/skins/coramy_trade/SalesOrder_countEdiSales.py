## Script (Python) "SalesOrder_countEdiSales"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
# Count the number of EDI sales order

number = 0
number_object = 0
number_sales_order = 0

object_list = context.object_action_list(selection_name='sales_order_selection')
for object in object_list:
    number_object += 1
    if object.getPortalType() == 'Sales Order':
        number_sales_order += 1
        print ':',
        print object.getCommandeOrigine(),
        if (object.getCommandeOrigine() == 'EDI'):
            number += 1
            print object.getId()

print '\n Total Commandes EDI: %i \n' % number
print '\n Total Commandes : %i \n' % number_object
print '\n Total Commandes Sales: %i \n' % number_sales_order

return printed
