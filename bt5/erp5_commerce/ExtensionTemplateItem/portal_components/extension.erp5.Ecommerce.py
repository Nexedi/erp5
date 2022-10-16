from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

from six.moves.urllib.parse import urlencode
import mechanize

def getProductPrice(product):
  getPrice = UnrestrictedMethod(product.getPrice)
  return getPrice()

def submitPaypalNVPRequest(parameter_dict, nvp_url):
  request = mechanize.Request(nvp_url)
  params = urlencode(parameter_dict)
  try:
    response = mechanize.urlopen(request, data=params)
  except:
    return None
  parameter_list = response.read().split('&')
  response_parameter_dict = {}
  for parameter in parameter_list:
    tmp = parameter.split('=')
    response_parameter_dict[tmp[0]] = tmp[1]
  return response_parameter_dict
