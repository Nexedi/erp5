##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
"""
Client implementation for portal_task_distribution.

Example use:
  import erp5.util.taskdistribution
  tool = erp5.util.taskdistribution.TaskDistributionTool(...)
  test_result = tool.createTestResult(...)
  test_result.addWatch('foo', open('foo'))
  while True:
      test_line = test_result.start()
      if not test_line:
          break
      # Run the test_line.name test
      test_line.stop()
"""
import logging
import select
import socket
import threading
import time
import xmlrpclib

__all__ = ['TaskDistributionTool', 'TestResultProxy', 'TestResultLineProxy', 'patchRPCParser']

# Depending on used xmlrpc backend, different exceptions can be thrown.
SAFE_RPC_EXCEPTION_LIST = [socket.error, xmlrpclib.ProtocolError,
    xmlrpclib.Fault]
parser, _ = xmlrpclib.getparser()
if xmlrpclib.ExpatParser and isinstance(parser, xmlrpclib.ExpatParser):
    SAFE_RPC_EXCEPTION_LIST.append(xmlrpclib.expat.ExpatError)
else:
    import sys
    print >> sys.stderr, 'Warning: unhandled xmlrpclib parser %r, some ' \
        'exceptions might get through safeRpcCall' % (parser, )
    del sys
SAFE_RPC_EXCEPTION_LIST = tuple(SAFE_RPC_EXCEPTION_LIST)
del parser, _

def null_callable(*args, **kw):
    pass

class NullLogger(object):
    def __getattr__(self, name):
        return null_callable
null_logger = NullLogger()

def patchRPCParser(error_handler):
    """
    Patch xmlrpcmlib's parser class, so it logs data content in case of errors,
    to ease debugging.
    Warning: this installs a monkey patch on a generic class, so it's last
    comes wins. Must *not* be enabled by default.

    error_handler (callable)
      Receives the erroneous data as first parameter, and the exception
      instance as second parameter.
      If it returns a false value (ie, handler did not recover from the error),
      exception is re-raised.
    """
    parser, _ = xmlrpclib.getparser()
    parser_klass = parser.__class__
    original_feed = parser_klass.feed
    def verbose_feed(self, data):
        try:
            return original_feed(self, data)
        except Exception, exc:
            if not error_handler(data, exc):
                raise
    parser_klass.feed = verbose_feed

class RPCRetry(object):
    def __init__(self, proxy, retry_time, logger, timeout=120):
        super(RPCRetry, self).__init__()
        self._proxy = proxy
        self._retry_time = retry_time
        self._logger = logger
        self.__rpc_lock = threading.Lock()
        self.timeout = timeout

    def _RPC(self, func_id, args=()):
            default_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.timeout)
            try:
                with self.__rpc_lock:
                    return getattr(self._proxy, func_id)(*args)
            finally:
                socket.setdefaulttimeout(default_timeout)

    def _retryRPC(self, func_id, args=()):
        retry_time = self._retry_time
        while True:
            try:
                return self._RPC(func_id, args)
            except SAFE_RPC_EXCEPTION_LIST:
                self._logger.warning('Got exception, retrying: %s%r '
                    'in %is', func_id, tuple(args), retry_time, exc_info=1)
                time.sleep(retry_time)
                retry_time *= 1.5

class TestResultLineProxy(RPCRetry):
    """
    Represents a single test in a suite.

    Properties:
    name (str) (ro)
      Test name, as provided to TaskDistributionTool.createTestResult .
    """
    def __init__(self, proxy, retry_time, logger, test_result_line_path,
            test_name):
        super(TestResultLineProxy, self).__init__(proxy, retry_time, logger)
        self._test_result_line_path = test_result_line_path
        self._name = test_name

    def __repr__(self):
        return '<%s(%r, %r) at %x>' % (self.__class__.__name__,
            self._test_result_line_path, self._name, id(self))

    @property
    def name(self):
        return self._name

    def stop(self, test_count=None, error_count=None, failure_count=None,
            skip_count=None, duration=None, date=None, command=None,
            stdout=None, stderr=None, html_test_result=None, **kw):
        """
        Notify server of test completion.

        Without any parameter, notifies of a test failure which prevents any
        precise reading (step count, how many succeeded, etc).

        BBB: extra named arguments are deprecated (if some are really needed,
        they must be declared as explicit parameters, with proper default
        value).
        """
        status_dict = dict(x for x in (
            ('test_count', test_count),
            ('error_count',  error_count),
            ('failure_count',  failure_count),
            ('skip_count',  skip_count),
            ('duration',  duration),
            ('date',  date),
            ('command',  command),
            ('stdout',  stdout),
            ('stderr',  stderr),
            ('html_test_result',  html_test_result),
        ) if x[1] is not None)
        if kw:
            self._logger.info('Extra parameters provided: %r', kw)
            status_dict.update(kw)
        self._retryRPC('stopUnitTest', (self._test_result_line_path,
            status_dict))

class TestResultProxy(RPCRetry):
    """
    Represents a test suite run.

    Allows fetching work to do (eg a single test in an entire run), monitoring
    log files, informing server of problems and monitoring server-side
    cancellation.

    Properties
    watcher_period (float) (rw)
      How long log watcher sleeps between successive uploading latest data
      chunks.
    revision (str) (ro)
      Revision to test. Might be different from the revision requested, when a
      test batch is running on an older revision.
    """
    _watcher_can_run = True
    _watcher_thread = None

    def __init__(self, proxy, retry_time, logger, test_result_path, node_title,
            revision):
        super(TestResultProxy, self).__init__(proxy, retry_time, logger)
        self._test_result_path = test_result_path
        self._node_title = node_title
        self._revision = revision
        self._watcher_period = 60
        self._watcher_dict = {}
        self._watcher_condition = threading.Condition()

    def __repr__(self):
        return '<%s(%r, %r, %r) at %x>' % (self.__class__.__name__,
            self._test_result_path, self._node_title, self._revision, id(self))

    @property
    def revision(self):
        return self._revision

    def start(self, exclude_list=()):
        """
        Ask for a test to run, among the list of tests composing this test
        result.
        Return an TestResultLineProxy instance, or None if there is nothing to
        do.
        """
        result = self._retryRPC('startUnitTest', (self._test_result_path,
            exclude_list))
        if result:
            line_url, test_name = result
            result = TestResultLineProxy(self._proxy, self._retry_time,
                self._logger, line_url, test_name)
        return result

    def reportFailure(self, date=None, command=None, stdout=None, stderr=None):
        """
        Report a test-node-level problem, preventing the test from continuing
        on this node.
        """
        self._stopWatching()
        status_dict = {
            'date': date,
        }
        if command is not None:
            status_dict['command'] = command
        if stdout is not None:
            status_dict['stdout'] = stdout
        if stderr is not None:
            status_dict['stderr'] = stderr
        self._retryRPC('reportTaskFailure', args=(self._test_result_path,
            status_dict, self._node_title))

    def reportStatus(self, command, stdout, stderr):
        """
        Report some progress.

        Used internally by file monitoring, you shouldn't have to use this
        directly.
        """
        try:
            self._RPC('reportTaskStatus', (self._test_result_path, {
                'command': command,
                'stdout': stdout,
                'stderr': stderr,
            }, self._node_title))
        except SAFE_RPC_EXCEPTION_LIST:
            self._logger.warning('Got exception in reportTaskStatus, giving up',
                exc_info=1)

    def isAlive(self):
        """
        Tell if test is still alive on site.

        Useful to probe for test cancellation by user, so a new test run can
        be started without waiting for current one to finish.
        """
        try:
            return self._RPC('isTaskAlive', (self._test_result_path, ))
        except SAFE_RPC_EXCEPTION_LIST:
            self._logger.warning('Got exception in isTaskAlive, assuming alive',
                exc_info=1)
            return 1

    @property
    def watcher_period(self):
        return self._watcher_period

    @watcher_period.setter
    def watcher_period(self, period):
        cond = self._watcher_condition
        with cond:
            self._watcher_period = period
            cond.notify()

    def addWatch(self, name, stream, max_history_bytes=None):
        """
        Monitor given file, sending a few latest lines to remote server.
        name (any)
          Arbitrary identifier for stream. Must be usable as a dict key.
        stream (file object)
          File to monitor from its current offset.
        max_history_bytes (int, None)
          How many bytes to send to remote server at most for each wakeup.
          If None, send all lines.
        """
        watcher_dict = self._watcher_dict
        if not watcher_dict:
            self._startWatching()
        elif name in watcher_dict:
            raise ValueError('Name already known: %r' % (name, ))
        watcher_dict[name] = (stream, max_history_bytes)

    def removeWatch(self, name):
        """
        Stop monitoring given stream.
        """
        watcher_dict = self._watcher_dict
        del watcher_dict[name]
        if not watcher_dict:
            self._stopWatching()

    def _startWatching(self):
        if self._watcher_thread is not None:
            raise ValueError('Thread already started')
        self._watcher_thread = thread = threading.Thread(target=self._watcher)
        thread.daemon = True
        thread.start()

    def _watcher(self):
        cond = self._watcher_condition
        while self._watcher_can_run and self.isAlive():
            working = time.time()
            caption_list = []
            append = caption_list.append
            for name, (stream, max_history_bytes) in \
                    self._watcher_dict.iteritems():
                append('==> %s <==' % (name, ))
                start = stream.tell()
                stream.seek(0, 2)
                end = stream.tell()
                if start == end:
                    caption = time.strftime(
                        '(no new lines at %Y/%m/%d %H:%M:%S)', time.gmtime())
                else:
                    to_read = end - start
                    if to_read < 0:
                        # File got truncated, treat the whole content as new.
                        to_read = end
                    if max_history_bytes is not None:
                        to_read = min(to_read, max_history_bytes)
                    stream.seek(-to_read, 1)
                    caption = stream.read(to_read)
                append(caption)
            self.reportStatus('', '\n'.join(caption_list), '')
            with cond:
                cond.wait(max(self._watcher_period - (working - time.time()),
                    0))

    def _stopWatching(self):
        cond = self._watcher_condition
        with cond:
            self._watcher_can_run = False
            cond.notify()
        self._watcher_thread.join()

class TaskDistributionTool(RPCRetry):
    def __init__(self, portal_url, retry_time=64, logger=None):
        """
        portal_url (str, None)
          Portal URL of ERP5 site to use as a task distributor.
          If None, single node setup is assumed.
        """
        if logger is None:
            logger = null_logger
        if portal_url is None:
            proxy = DummyTaskDistributionTool()
        else:
            proxy = xmlrpclib.ServerProxy(
                portal_url,
                allow_none=True,
            ).portal_task_distribution
        super(TaskDistributionTool, self).__init__(proxy, retry_time, logger)
        protocol_revision = self._retryRPC('getProtocolRevision')
        if protocol_revision != 1:
            raise ValueError('Unsupported protocol revision: %r',
                protocol_revision)

    def createTestResult(self, revision, test_name_list, node_title,
            allow_restart=False, test_title=None, project_title=None):
        """
        (maybe) create a new test run.
        revision (str)
          An opaque string describing code being tested.
        test_name_list (list of str)
          List of tests being part of this test run. May be empty.
        node_title (str)
          Human-readable test node identifier, so an adnmin can know which
          node does what.
        allow_restart (bool)
          When true, a tet result is always created, even if a former finished
          one is found for same name and revision pair.
        test_title (str)
          Human-readable title for test. Must be identical for successive runs.
          Allows browsing its result history.
        project_title (str)
          Existing project title, so test result gets associated to it.

        Returns None if no test run is needed (a test run for given name and
        revision has already been completed).
        Otherwise, returns a TestResultProxy instance.
        """
        result = self._retryRPC('createTestResult', ('', revision,
            test_name_list, allow_restart, test_title, node_title,
            project_title))
        if result:
            test_result_path, revision = result
            result = TestResultProxy(self._proxy, self._retry_time,
                self._logger, test_result_path, node_title, revision)
        return result

class DummyTaskDistributionTool(object):
    """
    Fake remote server.

    Useful when willing to locally run all tests without reporting to any
    server.

    This class should remain internal to this module.
    """
    test_name_list = None

    def __init__(self):
        self._lock = threading.Lock()

    def getProtocolRevision(self):
        return 1

    def createTestResult(self, name, revision, test_name_list, *args):
        self.test_name_list = test_name_list[:]
        return None, revision

    def startUnitTest(self, test_result_path, exclude_list=()):
        with self._lock:
            for i, test in enumerate(self.test_name_list):
                if test not in exclude_list:
                    del self.test_name_list[i]
                    return None, test

    def stopUnitTest(self, *args):
        pass

    reportTaskFailure = reportTaskStatus = stopUnitTest

    def isTaskAlive(self, *args):
        return int(bool(self.test_name_list))

