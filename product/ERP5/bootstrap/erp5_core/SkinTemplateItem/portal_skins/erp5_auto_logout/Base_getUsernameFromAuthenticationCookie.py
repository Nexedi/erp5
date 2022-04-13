from six.moves.urllib.parse import unquote
from base64 import standard_b64decode
from Products.ERP5Type.Utils import bytes2str
return bytes2str(standard_b64decode(unquote(value)).split(b':', 1)[0])
