context.REQUEST.set('editable_mode', 1)
person_object = context.getWebSiteValue().SaleOrder_getShoppingCartCustomer()
return context.getWebSectionValue().restrictedTraverse(person_object.getRelativeUrl()).Person_viewAsWeb(context.REQUEST)
