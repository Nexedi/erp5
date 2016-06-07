from urllib import unquote
return unquote(value).decode('base64').split(':', 1)[0]
