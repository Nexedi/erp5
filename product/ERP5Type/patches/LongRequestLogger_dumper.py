##############################################################################
#
# From Products.LongRequestLogger, adjusted for haufe.requestmonitoring
#
# Copyright (c) 2010,2012 Zope Foundation and Contributors.
#
##############################################################################

from pprint import pformat
import logging
import os
import sys
import time
import traceback

from six.moves import StringIO
from six.moves._thread import get_ident
from Products.ERP5Type.Utils import bytes2str

logger = logging.getLogger('Products.LongRequestLogger')


SUBJECT_FORMAT = "Thread %s: Started on %.1f; Running for %.1f secs; "
REQUEST_FORMAT = """\
request: %(method)s %(url)s
retry count: %(retries)s
form: %(form)s
other: %(other)s
"""

class Dumper(object):

    _last = None, None, None

    def __init__(self, thread_id):
        self.thread_id = thread_id

    def _format_request(self, request):
        if request is None:
            return "[No request]\n"
        try:
            query = request.get("QUERY_STRING")
            return REQUEST_FORMAT % {
                "method": request["REQUEST_METHOD"],
                "url": request.getURL() + ("?" + query if query else ""),
                "retries": request.retry_count,
                "form": pformat(request.form),
                "other": pformat(request.other),
            }
        except Exception:
            return "[Unprintable request]\n" + traceback.format_exc()

    # A fork of ZMySQLDA is maintained in ERP5 (http://www.erp5.com/)
    try:
        from Products.ZMySQLDA.db import DB
    except ImportError:
        def _extract_sql(self, frame):
            pass
    else:
        def _extract_sql(self, frame, func_code=DB._query.__code__):
            while frame is not None:
                if frame.f_code is func_code:
                    return bytes2str(frame.f_locals['query'])
                frame = frame.f_back
        del DB

    def format_log_entry(self, request, start, duration):
        subject = SUBJECT_FORMAT % (self.thread_id, start, duration)
        frame = sys._current_frames()[self.thread_id]
        try:
            request_text = self._format_request(request)
            stack = traceback.extract_stack(frame)
            query = self._extract_sql(frame)
        finally:
            del frame
        body = request_text, stack, query
        if self._last == body:
            return subject + "Same.\n"
        result = StringIO()
        result.write(subject)
        if request != self._last[0]:
            result.write(request_text)
        if stack != self._last[1]:
            result.write("Traceback:\n")
            traceback.print_list(stack, result)
        if query:
            result.write("SQL Query:%s\n" % (
                " Same." if query == self._last[2] else '\n' + query))
        self._last = body
        return result.getvalue()


class Handler(object):

    def __init__(self, config):
        self.config = config
        self.loglevel = int(getattr(logging, config.loglevel, logging.WARNING))
        self.dumpers_by_thread_id = {} # type: dict[int, Dumper]

    def __call__(self, req, handlerState, globalState):
        threadId = req.threadId
        try:
            dumper = self.dumpers_by_thread_id[threadId]
        except KeyError:
            dumper = self.dumpers_by_thread_id.setdefault(threadId, Dumper(threadId))
        log_entry = dumper.format_log_entry(req.request, req.startTime, handlerState.monitorTime - req.startTime)

        if os.environ.get('DISABLE_HAUFE_MONITORING_ON_PDB')\
                and log_entry.find("  Module pdb,") > -1:
            return
        logger.log(self.loglevel, log_entry)


def factory(config):
    """Factory to use with haufe.requestmonitoring (for zope.conf)
    """
    return Handler(config)
