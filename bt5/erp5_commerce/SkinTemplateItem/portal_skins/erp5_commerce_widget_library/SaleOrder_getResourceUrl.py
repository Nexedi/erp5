web_site = context.getWebSiteValue()
resource = context.getResourceValue()
web_site_product_line = web_site.getLayoutProperty('ecommerce_base_product_line')
portal_categories = context.getPortalObject().portal_categories
base_product_line_object = portal_categories.restrictedTraverse(web_site_product_line)

if resource in portal_categories.getRelatedValueList(base_product_line_object):
  return '%s/%s' % (context.getResourceValue().getRelativeUrl(), 'Resource_viewAsShop')
return None
