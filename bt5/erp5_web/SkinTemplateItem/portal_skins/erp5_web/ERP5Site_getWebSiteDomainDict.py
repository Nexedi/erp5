portal = context.getPortalObject()

# TODO: domain names should be exported to a web site property.
#   domain_dict = {}
#   for web_site in portal_catalog(portal_type="Web Site", validation_state="published"):
#     domain = web_site.getDomainName("")
#     if domain != "":
#       domain_dict[domain] = web_site
domain_dict = {
#  "domain.com": object,
}

# Try to add the domain name of the client REQUEST
root_object = portal.restrictedTraverse("/")
root_url = root_object.absolute_url()
if root_url.startswith("https://"):
  root_url = root_url[8:]
elif root_url.startswith("http://"):
  root_url = root_url[7:]
else:
  return domain_dict
domain_end = root_url.find("/")
if domain_end != -1:
  root_url = root_url[:domain_end]
if root_url and root_url not in domain_dict:
  domain_dict[root_url] = root_object
return domain_dict
