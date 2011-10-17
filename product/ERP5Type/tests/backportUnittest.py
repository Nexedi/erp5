# Backport of Python 2.7 unittest chosen parts to be able to use the
# "skip" decorators, and the associated ExpectedFailure and
# UnexpectedSuccess.
#
# Implementation is mostly a direct translation from Python r75708
# grep for "BACK" comments for backport-specific remarks.

import unittest
import sys
import time

class SkipTest(Exception):
    """
    Raise this exception in a test to skip it.

    Usually you can use TestResult.skip() or one of the skipping decorators
    instead of raising this directly.
    """
    pass

class _ExpectedFailure(Exception):
    """
    Raise this when a test is expected to fail.

    This is an implementation detail.
    """

    def __init__(self, exc_info):
        Exception.__init__(self)
        self.exc_info = exc_info

class _UnexpectedSuccess(Exception):
  """
  The test was supposed to fail, but it didn't!
  """
  pass

class SetupSiteError(Exception):
    """
    The ERP5 Site could not have been setup.
    This is raised when the site could not have been created in a previous
    test. We want this to count as an error, but we do not want this to happear
    in traceback for readability.
    """
    pass

def _id(obj):
    return obj

def skip(reason):
    """
    Unconditionally skip a test.
    """
    def decorator(test_item):
        if isinstance(test_item, type) and issubclass(test_item, TestCase):
            test_item.__unittest_skip__ = True
            test_item.__unittest_skip_why__ = reason
            return test_item
        def skip_wrapper(*args, **kwargs):
            raise SkipTest(reason)
        skip_wrapper.__name__ = test_item.__name__
        skip_wrapper.__doc__ = test_item.__doc__
        return skip_wrapper
    return decorator

def skipIf(condition, reason):
    """
    Skip a test if the condition is true.
    """
    if condition:
        return skip(reason)
    return _id

def skipUnless(condition, reason):
    """
    Skip a test unless the condition is true.
    """
    if not condition:
        return skip(reason)
    return _id


def expectedFailure(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            raise _ExpectedFailure(sys.exc_info())
        raise _UnexpectedSuccess
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

class TestCase(unittest.TestCase):
    """We redefine here the run() method, and add a skipTest() method.
    """

    failureException = AssertionError

    def run(self, result=None):
        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            # BACK: Not necessary for Python < 2.7:
            #       TestResult.startTestRun does not exist yet
            # startTestRun = getattr(result, 'startTestRun', None)
            # if startTestRun is not None:
            #    startTestRun()

        # BACK: Not needed for Python < 2.7
        #       unittest.addCleanup does not exist yet
        # self._resultForDoCleanups = result
        result.startTest(self)
        if getattr(self.__class__, "__unittest_skip__", False):
            # If the whole class was skipped.
            try:
                result.addSkip(self, self.__class__.__unittest_skip_why__)
            finally:
                result.stopTest(self)
            return
        testMethod = getattr(self, self._testMethodName)
        try:
            success = False
            try:
                self.setUp()
            except SkipTest, e:
                result.addSkip(self, str(e))
            except SetupSiteError, e:
                result.errors.append(None)
            except BaseException, e:
                result.addError(self, sys.exc_info())
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
            else:
                try:
                    testMethod()
                except self.failureException:
                    result.addFailure(self, sys.exc_info())
                except _ExpectedFailure, e:
                    result.addExpectedFailure(self, e.exc_info)
                except _UnexpectedSuccess:
                    result.addUnexpectedSuccess(self)
                except SkipTest, e:
                    result.addSkip(self, str(e))
                except BaseException, e:
                    result.addError(self, sys.exc_info())
                    if isinstance(e, (KeyboardInterrupt, SystemExit)):
                        raise
                else:
                    success = True

                try:
                    self.tearDown()
                except BaseException, e:
                    result.addError(self, sys.exc_info())
                    if isinstance(e, (KeyboardInterrupt, SystemExit)):
                        raise
                    success = False

            # BACK: Not needed for Python < 2.7
            #       unittest.addCleanup does not exist yet
            # cleanUpSuccess = self.doCleanups()
            # success = success and cleanUpSuccess
            if success:
                result.addSuccess(self)
        finally:
            result.stopTest(self)
            # BACK: Not necessary for Python < 2.7
            #       TestResult.stopTestRun does not exist yet
            # if orig_result is None:
            #    stopTestRun = getattr(result, 'stopTestRun', None)
            #    if stopTestRun is not None:
            #        stopTestRun()

    def skipTest(self, reason):
        """Skip this test."""
        raise SkipTest(reason)

    def defaultTestResult(self):
        return TestResult()

class TestResult(unittest.TestResult):
    def __init__(self):
        super(TestResult, self).__init__()
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []

    def addSkip(self, test, reason):
        """Called when a test is skipped."""
        self.skipped.append((test, reason))

    def addExpectedFailure(self, test, err):
        """Called when an expected failure/error occured."""
        self.expectedFailures.append(
            (test, self._exc_info_to_string(err, test)))

    def addUnexpectedSuccess(self, test):
        """Called when a test was expected to fail, but succeed."""
        self.unexpectedSuccesses.append(test)


class _TextTestResult(unittest._TextTestResult, TestResult):
    def __init__(self, stream, descriptions, verbosity):
        # BACK: nice diamond!
        #   unittest.TestResult.__init__ is called twice here
        unittest._TextTestResult.__init__(self, stream, descriptions, verbosity)
        TestResult.__init__(self)

    def addSkip(self, test, reason):
        super(_TextTestResult, self).addSkip(test, reason)
        if self.showAll:
            self.stream.writeln("skipped %s" % repr(reason))
        elif self.dots:
            self.stream.write("s")
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        super(_TextTestResult, self).addExpectedFailure(test, err)
        if self.showAll:
            self.stream.writeln("expected failure")
        elif self.dots:
            self.stream.write("x")
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        super(_TextTestResult, self).addUnexpectedSuccess(test)
        if self.showAll:
            self.stream.writeln("unexpected success")
        elif self.dots:
            self.stream.write("u")
            self.stream.flush()

    def printErrors(self):
        if self.dots or self.showAll:
            self.stream.writeln()
        # 'None' correspond to redundant errors due to site creation errors,
        # and we do not display them here.
        self.printErrorList('ERROR', filter(None, self.errors))
        self.printErrorList('FAIL', self.failures)
        if self.unexpectedSuccesses:
          self.stream.writeln(self.separator1)
          for test in self.unexpectedSuccesses:
            self.stream.writeln("SUCCESS: %s" % self.getDescription(test))

class TextTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return _TextTestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        result = self._makeResult()
        startTime = time.time()
        # BACK: 2.7 implementation wraps run with result.(start|stop)TestRun
        try:
          test(result)
        except KeyboardInterrupt:
          pass
        stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()
        results = map(len, (result.expectedFailures,
                            result.unexpectedSuccesses,
                            result.skipped))
        expectedFails, unexpectedSuccesses, skipped = results
        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        return result
