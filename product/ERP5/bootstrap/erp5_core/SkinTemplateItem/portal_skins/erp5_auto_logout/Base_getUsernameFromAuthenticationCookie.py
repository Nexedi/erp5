from future import standard_library
standard_library.install_aliases()
from urllib.parse import unquote
return unquote(value).decode('base64').split(':', 1)[0]
