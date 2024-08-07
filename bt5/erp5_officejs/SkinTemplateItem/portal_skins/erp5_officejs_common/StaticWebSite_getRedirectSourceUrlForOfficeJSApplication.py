"""
================================================================================
Redirect to domain specified as layout property on website
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------

import binascii
import base64
from Products.ERP5Type.Utils import bytes2str, str2bytes
import six

result_dict = {"error":"url missing definition view path"}
base_64 = False


try:
  name = context.REQUEST.other['source_path']
except KeyError:
  return result_dict

try:
  encoded = str2bytes(name.replace("definition_view/", "", 1))
  decode_method = base64.decodebytes if six.PY3 else base64.decodestring
  name = bytes2str(decode_method(encoded))
  base_64 = True
except binascii.Error:
  pass

if name.startswith("definition_view/") or name.startswith("portal_types/") or base_64:
  relative_url = name.replace("%2F", "/").replace("%20", " ")
  relative_url = relative_url.replace("definition_view/", "", 1)
  context.REQUEST.set("view", "definition_view")
  context.REQUEST.set("current_web_section", None)
  try:
    result_dict = context.getPortalObject().ERP5Document_getHateoas(mode="traverse", relative_url=relative_url, view="definition_view")
  except Exception as e:
    result_dict = {"error":"error while getting hateoas script for relative_url %s: %s" % (relative_url, str(e))}

return result_dict
