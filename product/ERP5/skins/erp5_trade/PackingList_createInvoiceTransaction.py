## Script (Python) "PackingList_createInvoiceTransaction"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
packing_list = context.getObject()
packing_list_type = packing_list.getPortalType()
packing_list_line_type = packing_list_type + ' Line'
transaction_module = context.getPortalObject().accounting
transaction_type = packing_list_type.split(' ')[0] + ' Invoice Transaction'
transaction_line_type = transaction_type + ' Line'

# Create a new transaction
new_id = str(transaction_module.generateNewId())
context.portal_types.constructContent(type_name=transaction_type,
        container=transaction_module,
        id=new_id,
        causality_title=context.getTitle(),
        title = packing_list.getTitle(),
        target_start_date = packing_list.getStartDate(),
        target_stop_date = packing_list.getStopDate(),
       )
transaction = transaction_module[new_id]

# Create each line
# If we do this before, each added line will take 20 times more time
# because of programmable acquisition
packing_list.edit(
        source = order.getSource(),
        destination = order.getDestination(),
        causality_value = packing_list
)
