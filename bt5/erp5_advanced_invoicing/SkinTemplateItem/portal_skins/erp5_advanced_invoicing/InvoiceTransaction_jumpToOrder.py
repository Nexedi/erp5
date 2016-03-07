"""Jump to the orders this invoice transaction was created from.
"""

invoice = context.getCausalityValue(portal_type=portal_type, checked_permission='View')

invoice.Invoice_jumpToOrder(packing_list_type=packing_list_type, order_type=order_type, form_id=form_id)
