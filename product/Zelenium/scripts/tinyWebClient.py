from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import sys
import http.client

if ( len(sys.argv) != 5 ):
    print("usage tinyWebClient.py host port method path")
else:
    host = sys.argv[1]
    port = sys.argv[2]
    method = sys.argv[3]
    path = sys.argv[4]

    info = (host, port)
    print("%s:%s" % info)
    conn = http.client.HTTPConnection("%s:%s" % info)
    conn.request(method, path)
    print(conn.getresponse().msg)
