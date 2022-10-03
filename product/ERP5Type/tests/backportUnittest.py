#from unittest import skip, skipIf, skipUnless, expectedFailure

class SetupSiteError(Exception):
    """
    The ERP5 Site could not have been setup.
    This is raised when the site could not have been created in a previous
    test. We want this to count as an error, but we do not want this to happear
    in traceback for readability.
    """

def patch():
    import six

    import traceback
    from unittest import TestCase, TextTestResult, TextTestRunner

    if six.PY3:
        TestCase.assertItemsEqual = TestCase.assertCountEqual

    TextTestResult_addError = six.get_unbound_function(TextTestResult.addError)
    def addError(self, test, err):
        if isinstance(err[1], SetupSiteError):
            self.errors.append(None)
        elif isinstance(err[1], SystemExit):
            raise err
        else:
            TextTestResult_addError(self, test, err)
    TextTestResult.addError = addError

    def wasSuccessful(self):
        "Tells whether or not this result was a success"
        return not (self.failures or self.errors or self.unexpectedSuccesses)
    TextTestResult.wasSuccessful = wasSuccessful

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
    TextTestResult.printErrors = printErrors

    TextTestRunner_run = six.get_unbound_function(TextTestRunner.run)
    def run(self, test):
        def t(result):
            try:
                test(result)
            except (KeyboardInterrupt, SystemExit):
                traceback.print_exc()
        return TextTestRunner_run(self, t)
    TextTestRunner.run = run

patch()
del patch
