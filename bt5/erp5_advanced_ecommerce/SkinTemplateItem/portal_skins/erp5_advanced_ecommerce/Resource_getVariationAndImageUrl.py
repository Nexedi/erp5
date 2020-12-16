"""
"""
from ZTUtils import make_query

url = context.absolute_url()
request = context.REQUEST
variation = request.get('variation', None)
if variation:
  parameter_string = make_query(variation=variation, image_id=image_id)
else:
  parameter_string = make_query(image_id=image_id)

# Use make_query
return "%s/Resource_viewAsShop?%s" % (url, parameter_string)
