"""
   DO NOT USE
   Each time the script is executed, a kitten dies.
   As URL generation is supposed to be separated from data manipulation
   to keep UI related code independant, no script should use both.
"""
from Products.ERP5Type.Utils import bytes2str, str2bytes
from base64 import urlsafe_b64encode
from ZTUtils import make_query
import json

make_query_kw = {
  'mode': 'traverse',
  'relative_url': context.getRelativeUrl(),
  'view': form_id,
}
if keep_items:
  make_query_kw['extra_param_json'] = bytes2str(urlsafe_b64encode(str2bytes(json.dumps(
    dict([(k, v) for k, v in keep_items.items() if k and v is not None])))))
return '#/%s?%s' % (
  context.getRelativeUrl(),
  make_query(
    view='%s/ERP5Document_getHateoas?%s' % (
      context.getWebSectionValue().absolute_url(),
      make_query(**make_query_kw),
    )),
)
