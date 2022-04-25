from six.moves.urllib.parse import unquote
from base64 import standard_b64decode
return standard_b64decode(unquote(value)).split(b':', 1)[0].decode()
