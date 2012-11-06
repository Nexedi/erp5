import re
from ZPublisher import HTTPResponse

_CRLF = re.compile(r'[\r\n]')
HTTPResponse._CRLF = _CRLF


if getattr(HTTPResponse, '_scrubHeader', None) is None:
    def _scrubHeader(name, value):
        return ''.join(_CRLF.split(str(name))), ''.join(_CRLF.split(str(value)))

    HTTPResponse.HTTPResponse.__old_setHeader = HTTPResponse.HTTPResponse.setHeader

    def setHeader(self, name, value, *args, **kwargs):
        name, value = _scrubHeader(name, value)
        return self.__old_setHeader(name, value, *args, **kwargs)
    HTTPResponse.HTTPResponse.setHeader = setHeader
