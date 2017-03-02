"""Set connected user as shopping cart customer"""
shopping_cart = context.SaleOrder_getShoppingCart()
member = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
shopping_cart.edit(destination_section_value=member)
