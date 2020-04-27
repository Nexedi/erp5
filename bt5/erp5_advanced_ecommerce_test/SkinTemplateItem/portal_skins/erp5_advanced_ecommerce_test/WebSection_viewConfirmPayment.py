person = context.ERP5Site_getAuthenticatedMemberPersonValue()

context.WebSection_persistShoppingCart(shopping_cart, person)

return context.Base_redirect('view',
                      keep_items={
                        "portal_status_message": "payment confirmed"
                      })
