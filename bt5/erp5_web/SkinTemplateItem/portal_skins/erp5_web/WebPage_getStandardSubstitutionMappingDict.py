# This is the standard version of text content substitution mapping method.
# This script returns commonly used keywords, and can be specified in Web Pages
# to substitute URLs embedded into the texts.
#
# Note: Please do not add rarely used ones into this script, because it becomes
# just an overhead for most pages. If you need more, it is better to create
# your own script instead.

website = context.getWebSiteValue()
if website is None:
  # handle the case when substitution happens on web page module context (i.e. reindex, or mass pre conversion)
  # then fall back to ERP5 site as a Web Site
  website = context.getPortalObject()
  return dict(website_url=website.absolute_url(),
              websection_url=website.absolute_url(),
              webpage_url=context.absolute_url())
else:
  websection = context.getWebSectionValue()
  return dict(website_url=website.absolute_url(),
              websection_url=websection.absolute_url(),
              webpage_url=websection.getPermanentURL(context))
