import argparse
from io import BytesIO
import logging
import os
import posixpath
import signal
import socket
import sys
from tempfile import TemporaryFile
import time
from urllib import quote, splitport

from waitress.server import create_server
import ZConfig
import Zope2
from Zope2.Startup.run import make_wsgi_app

from Products.ERP5Type.patches.WSGIPublisher import publish_module


# this class licensed under the MIT license (stolen from pyramid_translogger)
class TransLogger(object):

    format = ('%(REMOTE_ADDR)s - %(REMOTE_USER)s [%(time)s] '
              '"%(REQUEST_METHOD)s %(REQUEST_URI)s %(HTTP_VERSION)s" '
              '%(status)s %(bytes)s "%(HTTP_REFERER)s" "%(HTTP_USER_AGENT)s"')

    def __init__(self, application, logger):
        self.application = application
        self.logger = logger

    def __call__(self, environ, start_response):
        start = time.localtime()
        req_uri = quote(environ.get('SCRIPT_NAME', '')
                               + environ.get('PATH_INFO', ''))
        if environ.get('QUERY_STRING'):
            req_uri += '?'+environ['QUERY_STRING']
        method = environ['REQUEST_METHOD']
        def replacement_start_response(status, headers, exc_info=None):
            # @@: Ideally we would count the bytes going by if no
            # content-length header was provided; but that does add
            # some overhead, so at least for now we'll be lazy.
            bytes = None
            for name, value in headers:
                if name.lower() == 'content-length':
                    bytes = value
            self.write_log(environ, method, req_uri, start, status, bytes)
            return start_response(status, headers)
        return self.application(environ, replacement_start_response)

    def write_log(self, environ, method, req_uri, start, status, bytes):
        if bytes is None:
            bytes = '-'
        if time.daylight:
                offset = time.altzone / 60 / 60 * -100
        else:
                offset = time.timezone / 60 / 60 * -100
        if offset >= 0:
                offset = "+%0.4d" % (offset)
        elif offset < 0:
                offset = "%0.4d" % (offset)
        d = {
            'REMOTE_ADDR': environ.get('REMOTE_ADDR') or '-',
            'REMOTE_USER': environ.get('REMOTE_USER') or '-',
            'REQUEST_METHOD': method,
            'REQUEST_URI': req_uri,
            'HTTP_VERSION': environ.get('SERVER_PROTOCOL'),
            'time': time.strftime('%d/%b/%Y:%H:%M:%S ', start) + offset,
            'status': status.split(None, 1)[0],
            'bytes': bytes,
            'HTTP_REFERER': environ.get('HTTP_REFERER', '-'),
            'HTTP_USER_AGENT': environ.get('HTTP_USER_AGENT', '-'),
            }
        message = self.format % d
        self.logger.warn(message)


def app_wrapper(large_file_threshold=10<<20, webdav_ports=()):
    try:
        from Products.DeadlockDebugger.dumper import dump_threads, dump_url
    except Exception:
        dump_url = '\0'
    def app(environ, start_response):
        path_info = environ['PATH_INFO']
        if dump_url.startswith(path_info):
            query_string = environ['QUERY_STRING']
            if dump_url == (path_info + '?' + query_string if query_string
                            else path_info):
                start_response('200 OK', (('Content-type', 'text/plain'),))
                return [dump_threads()]

        original_wsgi_input = environ['wsgi.input']
        if not hasattr(original_wsgi_input, 'seek'):
            # Convert environ['wsgi.input'] to a file-like object.
            cl = environ.get('CONTENT_LENGTH')
            cl = int(cl) if cl else 0
            if cl > large_file_threshold:
                new_wsgi_input = environ['wsgi.input'] = TemporaryFile('w+b')
            else:
                new_wsgi_input = environ['wsgi.input'] = BytesIO()

            rest = cl
            chunksize = 1<<20
            try:
                while chunksize < rest:
                    new_wsgi_input.write(original_wsgi_input.read(chunksize))
                    rest -= chunksize
                if rest:
                    new_wsgi_input.write(original_wsgi_input.read(rest))
            except (socket.error, IOError):
                msg = b'Not enough data in request or socket error'
                start_response('400 Bad Request', [
                    ('Content-Type', 'text/plain'),
                    ('Content-Length', str(len(msg))),
                    ]
                )
                return [msg]
            new_wsgi_input.seek(0)

        if int(environ['SERVER_PORT']) in webdav_ports:
            # Munge the request to ensure that we call manage_FTPGet.

            # Set a flag to indicate this request came through the WebDAV source
            # port server.
            environ['WEBDAV_SOURCE_PORT'] = 1

            if environ['REQUEST_METHOD'] == 'GET':
                if os.sep != '/':
                    path_info =  path_info.replace(os.sep, '/')
                path_info = posixpath.join(path_info, 'manage_DAVget')
                path_info = posixpath.normpath(path_info)
                environ['PATH_INFO'] = path_info

        return publish_module(environ, start_response)
    return app

def createServer(application, logger, **kw):
    global server
    server = create_server(
        TransLogger(application, logger=logger),
        # We handle X-Forwarded-For by ourselves. See ERP5Type/patches/WSGITask.py.
        # trusted_proxy='*',
        # trusted_proxy_headers=('x-forwarded-for',),
        clear_untrusted_proxy_headers=True,
        **kw
    )
    if not hasattr(server, 'addr'):
      try:
        server.addr = kw['sockets'][0].getsockname()
      except KeyError:
        server.addr = server.adj.listen[0][3]
    elif not server.addr:
      server.addr = server.sockinfo[3]
    return server

def runwsgi():
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--webdav', action='store_true')
    parser.add_argument('address', help='<ip>:<port>')
    parser.add_argument('zope_conf', help='path to zope.conf')
    args = parser.parse_args()

    startup = os.path.dirname(Zope2.Startup.__file__)
    schema = ZConfig.loadSchema(os.path.join(startup, 'zopeschema.xml'))
    conf, _ = ZConfig.loadConfig(schema, args.zope_conf)

    make_wsgi_app({}, zope_conf=args.zope_conf)

    from Signals.SignalHandler import SignalHandler
    SignalHandler.registerHandler(signal.SIGTERM, sys.exit)

    ip, port = splitport(args.address)
    port = int(port)
    createServer(
        app_wrapper(
          large_file_threshold=conf.large_file_threshold,
          webdav_ports=[port] if args.webdav else ()),
        listen=args.address,
        logger=logging.getLogger("access"),
        threads=conf.zserver_threads,
    ).run()
