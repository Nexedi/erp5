# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: dumper.py,v 1.1 2005/02/23 15:35:21 fguillaume Exp $

"""Debug running threads

ZServer hook to dump a traceback of the running python threads.
"""

import thread
import threadframe
import traceback
import time
from cStringIO import StringIO

from zLOG import LOG, DEBUG

import custom


def dump_threads():
    """Dump running threads

    Returns a string with the tracebacks.
    """
    frames = threadframe.dict()
    this_thread_id = thread.get_ident()
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    res = ["Threads traceback dump at %s\n" % now]
    for thread_id, frame in frames.iteritems():
        if thread_id == this_thread_id:
            continue

        # Find request in frame
        reqinfo = ''
        f = frame
        while f is not None:
            co = f.f_code
            if (co.co_name == 'publish' and
                co.co_filename.endswith('/ZPublisher/Publish.py')):
                request = f.f_locals.get('request')
                if request is not None:
                    reqinfo = (request.get('REQUEST_METHOD', '') + ' ' +
                               request.get('PATH_INFO', ''))
                    qs = request.get('QUERY_STRING')
                    if qs:
                        reqinfo += '?'+qs
                break
            f = f.f_back
        if reqinfo:
            reqinfo = " (%s)" % reqinfo

        output = StringIO()
        traceback.print_stack(frame, file=output)
        res.append("Thread %s%s:\n%s" %
            (thread_id, reqinfo, output.getvalue()))

    frames = None
    res.append("End of dump")
    return '\n'.join(res)

dump_url = custom.DUMP_URL
if custom.SECRET:
    dump_url += '?'+custom.SECRET

def match(self, request):
    uri = request.uri

    # added hook
    if uri == dump_url:
        dump = dump_threads()
        request.channel.push('HTTP/1.0 200 OK\nContent-Type: text/plain\n\n')
        request.channel.push(dump)
        request.channel.close_when_done()
        LOG('DeadlockDebugger', DEBUG, dump)
        return 0
    # end hook

    if self.uri_regex.match(uri):
        return 1
    else:
        return 0

from ZServer.HTTPServer import zhttp_handler
zhttp_handler.match = match
