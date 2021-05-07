software_product = context
web_site = software_product.getFollowUpValue(portal_type="Web Section")

software_product.edit(reference=new_leaf_domain)
web_site.setId(new_leaf_domain)

return context.Base_redirect('view', keep_items=dict(portal_status_message="Application domain url updated"))
