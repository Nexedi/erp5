"""Set connected user as shopping cart customer"""
shopping_cart = context.SaleOrder_getShoppingCart()
member = context.ERP5Site_getAuthenticatedMemberPersonValue()
shopping_cart.edit(destination_section_value=member)
