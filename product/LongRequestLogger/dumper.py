##############################################################################
#
# Copyright (c) 2010,2012 Zope Foundation and Contributors.
#
##############################################################################

from cStringIO import StringIO
from pprint import pformat
from thread import get_ident
import Signals.Signals
import ZConfig.components.logger.loghandler
import ZServer.BaseLogger
import logging
import os
import os.path
import time
import traceback
import sys

try:
    from signal import SIGUSR2
except ImportError:
    # Windows doesn't have these (but also doesn't care what the exact
    # numbers are)
    SIGUSR2 = 12

try:
    sys._current_frames
except AttributeError:
    # Python 2.4 and older
    import threadframe
    sys._current_frames = threadframe.dict


class NullHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        # for comparison purposes below
        self.baseFilename = 'null'

    def emit(self, *args, **kw):
        pass


# we might want to change this name later to something more specific
logger_name = __name__
log = logging.getLogger(logger_name)
log.propagate = False
handler = NullHandler()
log.addHandler(handler)

formatter = logging.Formatter("%(asctime)s - %(message)s")

DEFAULT_TIMEOUT = 2
DEFAULT_INTERVAL = 1

def do_enable():
    global handler
    # this function is not exactly thread-safe, but it shouldn't matter.
    # The worse that can happen is that a change in longrequestlogger_file
    # will stop or change the logging destination of an already running request
    logfile = os.environ.get('longrequestlogger_file')
    if not logfile:
        return None # so that Dumpers know they are disabled

    if logfile != 'null':
        # to imitate FileHandler
        logfile = os.path.abspath(logfile)

    rotate = None
    if handler.baseFilename != logfile:
        log.removeHandler(handler)
        handler.close()
        if logfile == 'null':
            handler = NullHandler()
        elif os.name == 'nt':
            rotate = Signals.Signals.LogfileRotateHandler
            handler = ZConfig.components.logger.loghandler.Win32FileHandler(
                logfile)
        else:
            rotate = Signals.Signals.LogfileReopenHandler
            handler = ZConfig.components.logger.loghandler.FileHandler(
                logfile)
        handler.formatter = formatter
        log.addHandler(handler)

    # Register with Zope 2 signal handlers to support log rotation
    if rotate and Signals.Signals.SignalHandler:
        Signals.Signals.SignalHandler.registerHandler(
            SIGUSR2, rotate([handler]))
    return log # which is also True as boolean

def get_configuration():
    return dict(
        timeout=float(os.environ.get('longrequestlogger_timeout', 
                                       DEFAULT_TIMEOUT)),
        interval=float(os.environ.get('longrequestlogger_interval', 
                                       DEFAULT_INTERVAL)),
    )

THREAD_FORMAT = "Thread %s: Started on %.1f; Running for %.1f secs; %s"
REQUEST_FORMAT = """
request: %(method)s %(url)s
retry count: %(retries)s
form: %(form)s
other: %(other)s
""".strip()

class Dumper(object):

    def __init__(self, thread_id=None):
        if thread_id is None:
            # assume we're being called by the thread that wants to be
            # monitored
            thread_id = get_ident()
        self.thread_id = thread_id
        self.start = time.time()
        # capture it here in case it gets disabled in the future
        self.log = do_enable()
        conf = get_configuration()
        self.timeout = conf['timeout']
        self.interval = conf['interval']

    def is_enabled(self):
        return bool(self.log)

    def format_request(self, request):
        if request is None:
            return "[No request]"
        url = request.getURL()
        if request.get('QUERY_STRING'):
            url += '?' + request['QUERY_STRING']
        retries = request.retry_count
        method = request['REQUEST_METHOD']
        form = pformat(request.form)
        other = pformat(request.other)
        return REQUEST_FORMAT % locals()

    def extract_request(self, frame):
        # We try to fetch the request from the 'call_object' function because
        # it's the one that gets called with retried requests.
        # And we import it locally to get even monkey-patched versions of the
        # function.
        from ZPublisher.Publish import call_object
        func_code = call_object.func_code #@UndefinedVariable
        while frame is not None:
            code = frame.f_code
            if (code is func_code):
                request = frame.f_locals.get('request')
                return request
            frame = frame.f_back

    def extract_request_info(self, frame):
        request = self.extract_request(frame)
        return self.format_request(request)

    def get_thread_info(self, frame):
        request_info = self.extract_request_info(frame)
        now = time.time()
        runtime = now - self.start
        info = THREAD_FORMAT % (self.thread_id,
                                self.start,
                                runtime,
                                request_info)
        return info

    def format_thread(self):
        frame = sys._current_frames()[self.thread_id]
        output = StringIO()
        thread_info = self.get_thread_info(frame)
        print >> output, thread_info
        print >> output, "Traceback:"
        traceback.print_stack(frame, file=output)
        try:
          from Products.ZMySQLDA.db import DB
          while frame is not None:
            code = frame.f_code
            if code is DB._query.func_code:
              print >> output, "SQL Query:"
              print >> output, frame.f_locals['query']
            frame = frame.f_back
        except ImportError:
          pass
        del frame
        return output.getvalue()

    def __call__(self):
        self.log.warning(self.format_thread())
