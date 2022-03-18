#from unittest import skip, skipIf, skipUnless, expectedFailure

class SetupSiteError(Exception):
    """
    The ERP5 Site could not have been setup.
    This is raised when the site could not have been created in a previous
    test. We want this to count as an error, but we do not want this to happear
    in traceback for readability.
    """

def patch():
    import traceback
    from unittest import TextTestResult, TextTestRunner

    TextTestResult_addError = TextTestResult.addError
    import six
    if six.PY2:
      TextTestResult_addError = TextTestResult_addError.__func__
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
        self.printErrorList('ERROR', [_f for _f in self.errors if _f])
        self.printErrorList('FAIL', self.failures)
        if self.unexpectedSuccesses:
          self.stream.writeln(self.separator1)
          for test in self.unexpectedSuccesses:
            self.stream.writeln("SUCCESS: %s" % self.getDescription(test))
    TextTestResult.printErrors = printErrors

    TextTestRunner_run = TextTestRunner.run
    import six
    if six.PY2:
        TextTestRunner_run = TextTestRunner_run.__func__
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
