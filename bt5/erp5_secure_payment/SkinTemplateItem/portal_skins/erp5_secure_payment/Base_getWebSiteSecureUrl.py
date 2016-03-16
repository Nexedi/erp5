"""Return the secure url of current web site based on layout configuration"""

website = context.getWebSiteValue()
return website.getLayoutProperty('layout_secure_url', website.getAbsoluteUrl())
