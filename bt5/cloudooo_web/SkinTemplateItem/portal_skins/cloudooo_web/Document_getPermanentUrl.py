website_url = "http://www.cloudooo.com"
try:
  website_url = context.getWebSiteValue().absolute_url()
except AttributeError:
  pass
param, key = context.getContributorValue().WebSite_getUserAuthentificationKey()

return "%s?%s=%s" % (website_url,param,key)
