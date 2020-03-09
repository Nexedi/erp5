"""
 This will return all Products that have set product_line='shipping'. XXX
 Such products are used for shipping purposes i.e. they can not be sold.
"""
portal = context.getPortalObject()

# XXX hardcoded category
shipping_product_line_category_uid = portal.portal_categories.product_line.shipping.getUid()

return [r.getObject() for r in portal.portal_catalog(
                 product_line_uid=shipping_product_line_category_uid,
                 portal_type=portal.getPortalResourceTypeList(),
                 validation_state=("validated", "published")
)]
