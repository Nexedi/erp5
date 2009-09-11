# -*- coding: UTF-8 -*-
# -*- Mode: Python; py-indent-offset: 4 -*-
# Authors: Nik Kim <fafhrd@legco.biz>
__version__ = 'TimerServer for Zope 0.1'

import traceback

import thread
import re
import sys, os, errno, time, socket
from StringIO import StringIO
from zLOG import LOG, INFO

from ZServer.PubCore import handle
from ZPublisher.BaseRequest import BaseRequest
from ZPublisher.BaseResponse import BaseResponse
from ZPublisher.HTTPRequest import HTTPRequest
import ZPublisher.HTTPRequest

class TimerServer:
    def __init__(self, module, interval=600):
        self.module = module

        self.interval = interval

        sync = thread.allocate_lock()

        self._a = sync.acquire
        self._r = sync.release

        self._a()
        thread.start_new_thread(self.run, ())
        self._r()

        LOG('ZServer', INFO,
            'Timer server started at %s\n'
            '\tInterval: %s seconds.\n'%(time.ctime(time.time()), interval))

    def run(self):
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

        # minutes = time.gmtime(time.time()[4], seconds = time.gmtime(time.time()[5]
        # max interval is therefore 59*60 + 59 = 208919 seconds

        wait = ((time.gmtime(time.time())[4] * 60) + time.gmtime(time.time())[5]) % interval
        sleep = interval - wait

        if sleep > 0:
            time.sleep(sleep)

        LOG('ZServer', INFO, 'Timerserver ready, starting timer services.')

        while 1:
            time.sleep(interval)
            # send message to zope
            try:
                out = StringIO()
                err = StringIO()
                response = TimerResponse(out, err)
                handle(module, TimerRequest(response, interval), response)
            except:
                pass


class TimerResponse(BaseResponse):
    def _finish(self):
        pass

    def unauthorized(self):
        pass

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
        if self.headers.has_key('content-type'):
            match = charset_re.match(self.headers['content-type'])
            if match:
                encoding = match.group(1)
                return body.encode(encoding)
        # Use the default character encoding
        return body.encode(ZPublisher.HTTPResponse.default_encoding,'replace')


class TimerRequest(HTTPRequest):

    retry_max_count = 0

    def __init__(self, response, interval):
        stdin=StringIO()
        environ=self._get_env(stdin)
        HTTPRequest.__init__(self, stdin, environ, response, clean=1)

        self.other['interval'] = interval

    def _get_env(self, stdin):
        "Returns a CGI style environment"
        env={}
        env['REQUEST_METHOD']='GET'
        env['SERVER_SOFTWARE']= 'TimerServer for Zope'
        env['SERVER_NAME'] = ''
        env['SERVER_PORT'] = ''
        env['REMOTE_ADDR'] = ''
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'

        env['PATH_INFO']= '/Control_Panel/timer_service/process_timer'
        return env
