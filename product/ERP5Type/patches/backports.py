##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from ZPublisher.WSGIPublisher import WSGIResponse

# PATCH 1
#
# According to PEP 333, WSGI applications and middleware are forbidden from
# using HTTP/1.1 "hop-by-hop" features or headers. This patch prevents Zope
# from sending 'Connection' and 'Transfer-Encoding' headers.
#
# The following code is a backport from Zope 4.0b1, see commit
# be5b14bd858da787c41a39e2533b0aabcd246fd5.
def finalize(self):

    headers = self.headers
    body = self.body

    # There's a bug in 'App.ImageFile.index_html': when it returns a 304 status
    # code, 'Content-Length' is equal to a nonzero value.
    if self.status == 304:
      headers.pop('content-length', None)

    # set 204 (no content) status if 200 and response is empty
    # and not streaming
    if ('content-type' not in headers and
            'content-length' not in headers and
            not self._streaming and self.status == 200):
        self.setStatus('nocontent')

    # add content length if not streaming
    content_length = headers.get('content-length')

    if content_length is None and not self._streaming:
        self.setHeader('content-length', len(body))

    return '%s %s' % (self.status, self.errmsg), self.listHeaders()

WSGIResponse.finalize = finalize
