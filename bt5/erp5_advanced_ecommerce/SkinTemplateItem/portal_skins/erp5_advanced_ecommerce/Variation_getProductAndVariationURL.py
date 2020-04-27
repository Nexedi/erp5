"""
  Generate a URL based on the parent resource with
  default variation as parameter

  TODO:
  - make generic and move to erp5_commerce
"""
url = context.getParentValue().absolute_url()
variation = context.getRelativeUrl()
from ZTUtils import make_query
parameter_string = make_query(variation=variation)

# Use make_query
return "%s/Resource_viewAsShop?%s" % (url, parameter_string)
