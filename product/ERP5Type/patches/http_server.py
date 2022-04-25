# This code is taken from the medusa in zope 2.8.
#
# The license term should be this one:
#
# Medusa is Copyright 1996-2000, Sam Rushing &lt;rushing@nightmare.com&gt;
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Sam
# Rushing not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.

#   Author: Sam Rushing <rushing@nightmare.com>
#   Copyright 1996-2000 by Sam Rushing
#                        All Rights Reserved.


from ZServer.medusa.http_server import http_request
import ZPublisher.HTTPRequest
import string
import base64
import time
from six.moves.urllib.parse import quote

def log (self, bytes):
    addr = self.channel.addr[0]
    # Frontend-facing proxy is responsible for sanitising
    # HTTP_X_FORWARDED_FOR, and only trusted accesses should bypass
    # that proxy. So trust first entry.
    #
    # <patch>
    if ZPublisher.HTTPRequest.trusted_proxies == ('0.0.0.0',): # Magic value to enable this functionality
      forwarded_for = (self.get_header('x-forwarded-for') or '').split(',', 1)[0].strip()
      if forwarded_for:
        addr = forwarded_for
    # </patch>

    user_agent=self.get_header('user-agent')
    if not user_agent: user_agent=''
    referer=self.get_header('referer')
    if not referer: referer=''

    auth=self.get_header('Authorization')
    name='Anonymous'
    if auth is not None:
        if string.lower(auth[:6]) == 'basic ':
            try: decoded=base64.decodestring(auth[6:])
            except base64.binascii.Error: decoded=''
            t = string.split(decoded, ':', 1)
            if len(t) < 2:
                name = 'Unknown (bad auth string)'
            else:
                name = t[0]

    # Originally, an unquoted request string was logged, but
    # it only confuses log analysis programs! Note that Apache
    # HTTP Server never unquote URIs in the access log.
    t = self.request.split(' ')
    quoted_request = '%s %s %s' % (t[0], quote(' '.join(t[1:-1])), t[-1])

    self.channel.server.logger.log (
        # <patch>
        addr,
        # </patch>
        '- %s [%s] "%s" %d %d "%s" "%s"\n' % (
            name,
            self.log_date_string (time.time()),
            # <patch>
            quoted_request,
            # </patch>
            self.reply_code,
            bytes,
            referer,
            user_agent
            )
        )

http_request.log = log
