software_product = context
web_site = software_product.getFollowUpValue(portal_type="Web Section")

software_product.setReference(new_url_domain)
web_site.setId(new_url_domain)
software_product.setFollowUpValue(web_site)

return context.Base_redirect('view', keep_items=dict(portal_status_message="Application domain url updated"))
