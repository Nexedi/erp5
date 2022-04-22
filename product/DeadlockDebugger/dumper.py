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

import six
import _thread
from sys import _current_frames
import traceback
import time
from io import BytesIO

from zLOG import LOG, DEBUG, ERROR
from App.config import getConfiguration

def dump_threads():
    """Dump running threads

    Returns a string with the tracebacks.
    """
    this_thread_id = thread.get_ident()
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    res = ["Threads traceback dump at %s\n" % now]
    for thread_id, frame in _current_frames().iteritems():
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

        mysql_info = ''
        f = frame
        try:
          from Products.ZMySQLDA.db import DB
          while f is not None:
            code = f.f_code
            if code is DB._query.__code__:
              mysql_info = "\nMySQL query:\n%s\n" % f.f_locals['query']
              break
            f = f.f_back
        except ImportError:
          pass

        output = BytesIO()
        traceback.print_stack(frame, file=output)
        res.append("Thread %s%s:\n%s%s" %
            (thread_id, reqinfo, output.getvalue(), mysql_info))

    res.append("End of dump\n")
    result = '\n'.join(res)
    if isinstance(result, six.text_type):
      result = result.encode('utf-8')
    return result

config = getConfiguration()
deadlockdebugger = config.product_config.get('deadlockdebugger')
dump_url = ''
secret = ''
dump_url = deadlockdebugger['dump_url']
secret = deadlockdebugger.get('secret', '')

if dump_url and secret:
    dump_url += '?'+secret

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
import six
if six.PY2:
  from ZServer.HTTPServer import zhttp_handler
  zhttp_handler.match = match
