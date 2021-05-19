software_product = context
software_product.edit(reference=new_leaf_domain)
#setReference interaction workflow will update the corresponding web site

return context.Base_redirect('view', keep_items=dict(portal_status_message="Application domain url updated"))
