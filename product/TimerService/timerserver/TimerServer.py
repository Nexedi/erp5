# -*- coding: UTF-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
# Authors: Nik Kim <fafhrd@legco.biz>

import errno, logging, os, re, socket, sys, threading, time, traceback
from functools import partial
from urllib.parse import urlsplit
from io import StringIO

from ZPublisher.BaseResponse import BaseResponse
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
import ZPublisher.HTTPRequest

logger = logging.getLogger('TimerServer')

class TimerServer(threading.Thread):

    def __init__(self, module, interval=600):
        super(TimerServer, self).__init__()
        self.daemon = True
        self.module = module
        self.interval = interval
        self.start()
        logger.info('Service initialized with interval of %s second(s).',
                    interval)

    def run(self):
        try:
            zopewsgi = sys.modules['Products.ERP5.bin.zopewsgi']
        except KeyError:
            # wait until the zhttp_server exist in socket_map
            # because TimerService has to be started after the Zope HTTPServer
            from asyncore import socket_map
            ip = port = ''
            while 1:
                time.sleep(5)
                for k, v in socket_map.items():
                    if hasattr(v, 'addr'):
                        # see Zope/lib/python/App/ApplicationManager.py: def getServers(self)
                        type = str(getattr(v, '__class__', 'unknown'))
                        if type == 'ZServer.HTTPServer.zhttp_server':
                            ip, port = v.addr
                            break
                if port:
                    break
            from ZServer.PubCore import handle
        else:
            while 1:
                time.sleep(5)
                try:
                    server = zopewsgi.server
                    break
                except AttributeError:
                    pass

            ip, port = server.addr
            start_response = lambda *_: None

            class handle(object):
                def __init__(self, module_name, request, response):
                    self.service = partial(zopewsgi.publish_module,
                        request.environ,
                        start_response,
                        _module_name=module_name,
                        _request=request,
                        _response=response)
                    server.add_task(self)

                def cancel(self):
                    pass

        if ip == '0.0.0.0':
          ip = socket.gethostbyname(socket.gethostname())

        # To be very sure, try to connect to the HTTPServer
        # and only start after we are able to connect and got a response
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(None)
        while 1:
            try:
                s.connect((ip, port))
            except socket.error:
                time.sleep(5)
                continue
            s.send('GET / HTTP/1.1\r\n\r\n')
            s.recv(4096) # blocks until a response is received
            break
        s.close()

        module = self.module
        interval = self.interval

        logger.info('Service ready.')

        while 1:
            time.sleep(interval)
            # send message to zope
            try:
                out = StringIO()
                err = StringIO()
                response = TimerResponse(out, err)
                handle(module, TimerRequest(response, interval), response)
            except Exception:
                logger.warn("Ignoring exception in run loop", exc_info=True)


TIMER_SERVICE_PATH = '/Control_Panel/timer_service'
TIMER_ENVIRON = {
    'REQUEST_METHOD': 'GET',
    'SERVER_SOFTWARE': 'TimerServer for Zope',
    'SERVER_NAME': '',
    'SERVER_PORT': '-1',
    'REMOTE_ADDR': '',
    'GATEWAY_INTERFACE': 'CGI/1.1',
    'SERVER_PROTOCOL': 'HTTP/1.0',
    'PATH_INFO': TIMER_SERVICE_PATH + '/process_timer',
}


class TimerResponse(BaseResponse):

    after_list = ()

    def _finish(self):
        pass

    def unauthorized(self):
        pass

    def _unauthorized(self):
        pass

    def finalize(self):
        return None, None

    # This is taken from ZPublisher.HTTPResponse
    # I don't think it's safe to make TimerResponse a subclass of HTTPResponse,
    # so I inline here the method . This is required it you want unicode page
    # templates to be usable by timer service.
    # This is used by an iHotFix patch on PageTemplate.StringIO method
    def _encode_unicode(self, body,
                        charset_re=re.compile(r'(?:application|text)/[-+0-9a-z]+\s*;\s*' +
                                              r'charset=([-_0-9a-z]+' +
                                              r')(?:(?:\s*;)|\Z)',
                                              re.IGNORECASE)):
        # Encode the Unicode data as requested
        if 'content-type' in self.headers:
            match = charset_re.match(self.headers['content-type'])
            if match:
                encoding = match.group(1)
                return body.encode(encoding)
        # Use the default character encoding
        return body.encode(ZPublisher.HTTPResponse.default_encoding,'replace')

    def notFoundError(self, url):
        assert urlsplit(url).path == TIMER_SERVICE_PATH, url
        return lambda: None


class TimerRequest(HTTPRequest):

    retry_max_count = 0

    def __init__(self, response, interval):
        stdin=StringIO()
        environ=self._get_env(stdin)
        HTTPRequest.__init__(self, stdin, environ, response, clean=1)

        self.other['interval'] = interval

    def _get_env(self, stdin):
        "Returns a CGI style environment"
        return TIMER_ENVIRON.copy()

    def clone(self):
        # This method is a dumb copy of Zope-2.8's one that makes timerserver
        # works in Zope-2.12 too.
        #
        # Return a clone of the current request object
        # that may be used to perform object traversal.
        environ = self.environ.copy()
        environ['REQUEST_METHOD'] = 'GET'
        if self._auth:
            environ['HTTP_AUTHORIZATION'] = self._auth
        clone = HTTPRequest(None, environ, HTTPResponse(), clean=1)
        clone['PARENTS'] = [self['PARENTS'][-1]]
        return clone
