##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                     Kazuhiko <kazuhiko@nexedi.com>
#                     Rafael Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
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

import os
import signal
import sys
import time
import re
import subprocess
import shutil
import transaction
from ZPublisher.HTTPResponse import HTTPResponse
from zExceptions.ExceptionFormatter import format_exception
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase, \
                                               _getConversionServerDict
from Products.ERP5Type.Utils import stopProcess, PR_SET_PDEATHSIG
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# REGEX FOR ZELENIUM TESTS
TEST_PASS_RE = re.compile('<th[^>]*>Tests passed</th>\n\s*<td[^>]*>([^<]*)')
TEST_FAILURE_RE = re.compile('<th[^>]*>Tests failed</th>\n\s*<td[^>]*>([^<]*)')
IMAGE_RE = re.compile('<img[^>]*?>')
TEST_ERROR_TITLE_RE = re.compile('(?:error.gif.*?>|title status_failed"><td[^>]*>)([^>]*?)</td></tr>', re.S)
TEST_RESULT_RE = re.compile('<div style="padding-top: 10px;">\s*<p>\s*'
                          '<img.*?</div>\s.*?</div>\s*', re.S)

TEST_ERROR_RESULT_RE = re.compile('.*(?:error.gif|title status_failed).*', re.S)
EXPECTED_FAILURE_RE = re.compile('.*expected failure.*', re.I)

ZELENIUM_BASE_URL = "%s/portal_tests/%s/core/TestRunner.html?test=../test_suite_html&auto=on&resultsUrl=../postResults&__ac_name=%s&__ac_password=%s"

tests_framework_home = os.path.dirname(os.path.abspath(__file__))
# handle 'system global' instance
if tests_framework_home.startswith('/usr/lib'):
  real_instance_home = '/var/lib/erp5'
else:
  real_instance_home = os.path.sep.join(
    tests_framework_home.split(os.path.sep)[:-3])

instance_home = os.path.join(real_instance_home, 'unit_test')
bt5_dir_list = ','.join([
                    os.path.join(instance_home, 'Products/ERP5/bootstrap'),
                    os.path.join(instance_home, 'bt5')])

class TimeoutError(Exception):
  pass

class Process(object):

  def preexec_fn(self):
    PR_SET_PDEATHSIG(signal.SIGTERM)

  def _exec(self, *args, **kw):
    self.process = subprocess.Popen(preexec_fn=self.preexec_fn, *args, **kw)

  def quit(self):
    if hasattr(self, 'process'):
      stopProcess(self.process)
      del self.process

class Xvfb(Process):
  def __init__(self, fbdir):
    self.display_list = [":%s" % i for i in range(123, 144)]
    self.display = None
    self.fbdir = fbdir

  def _runCommand(self, display):
    xvfb_bin = os.environ.get("xvfb_bin", "Xvfb")
    with open(os.devnull, 'w') as null:
      self._exec(
        (xvfb_bin, '-fbdir' , self.fbdir, display,
        '-screen', '0', '1280x1024x24'),
        stdout=null, stderr=null, close_fds=True)
      # try to check if X screen is available
      time.sleep(5)
      return
      # XXX xdpyinfo is not installed yet. Is this checking really needed ?
      # If it is required, we have to make xdpyinfo available as part of
      # selinum runner and make testnode using it (testnode use the software
      # of selenium runner to launch firefox and Xvfb)
      """
      if subprocess.call(('xdpyinfo', '-display', display),
                         stdout=null, stderr=subprocess.STDOUT):
        # Xvfb did not start properly so stop here
        raise EnvironmentError("Can not start Xvfb, stop test execution " \
                               + "(display %r)" % (display,))
      """

  def run(self):
    for display_try in self.display_list:
      lock_filepath = '/tmp/.X%s-lock' % display_try.replace(":", "")
      if not os.path.exists(lock_filepath):
        self._runCommand(display_try)
        self.display = display_try
        os.environ['DISPLAY'] = self.display
        break
    else:
      raise EnvironmentError("All displays locked : %r" % (self.display_list,))

    print 'Xvfb : %d' % self.process.pid
    print 'Take screenshots using xwud -in %s/Xvfb_screen0' % self.fbdir

class FunctionalTestRunner:

  # There is no test that can take more than 6 hours
  timeout = 6.0 * 3600

  def __init__(self, host, port, portal, run_only=''):
    self.instance_home = os.environ['INSTANCE_HOME']

    # Such information should be automatically loaded
    self.user = 'ERP5TypeTestCase'
    self.password = ''
    self.run_only = run_only
    profile_dir = os.path.join(self.instance_home, 'profile')
    self.portal = portal

  def getStatus(self):
    transaction.begin()
    return self.portal.portal_tests.TestTool_getResults(self.run_only)

  def _getTestURL(self):
    return ZELENIUM_BASE_URL % (self.portal.portal_url(), self.run_only,
                       self.user, self.password)

  def test(self, debug=0):
    xvfb = Xvfb(self.instance_home)
    try:
      if not debug:
        print("\nSet 'erp5_debug_mode' environment variable to 1"
              " to use your existing display instead of Xvfb.")
        xvfb.run()
      firefox_bin = os.environ.get("firefox_bin") 
      firefox_driver = firefox_bin.replace("firefox-slapos", "geckodriver")
      firefox_capabilities = webdriver.common.desired_capabilities.DesiredCapabilities.FIREFOX
      firefox_capabilities['marionette'] = True
      firefox_capabilities['binary'] = firefox_bin
      browser = webdriver.Firefox(capabilities=firefox_capabilities, executable_path=firefox_driver)
      start_time = time.time()
      browser.get(self._getTestURL())

      WebDriverWait(browser, 10).until(EC.presence_of_element_located((
        By.XPATH, '//iframe[@id="testSuiteFrame"]'
      )))
      # XXX No idea how to wait for the iframe content to be loaded
      time.sleep(5)
      # Count number of test to be executed
      test_count = browser.execute_script(
        "return document.getElementById('testSuiteFrame').contentDocument.querySelector('tbody').children.length"
      ) - 1
      WebDriverWait(browser, self.timeout).until(EC.presence_of_element_located((
        By.XPATH, '//td[@id="testRuns" and contains(text(), "%i")]' % test_count
      )))
    finally:
      xvfb.quit()

  def processResult(self):
    file_content = self.getStatus().encode("utf-8", "replace")
    sucess_amount = int(TEST_PASS_RE.search(file_content).group(1))
    failure_amount = int(TEST_FAILURE_RE.search(file_content).group(1))
    error_title_list = [re.compile('\s+').sub(' ', x).strip()
                    for x in TEST_ERROR_TITLE_RE.findall(file_content)]

    is_expected_failure = lambda x: EXPECTED_FAILURE_RE.match(x)
    expected_failure_amount = len(filter(is_expected_failure, error_title_list))
    # Remove expected failures from list
    error_title_list = filter(lambda x: not is_expected_failure(x), error_title_list)
    failure_amount -= expected_failure_amount

    detail = ''
    for test_result in TEST_RESULT_RE.findall(file_content):
      if TEST_ERROR_RESULT_RE.match(test_result):
        detail += test_result

    detail = IMAGE_RE.sub('', detail)
    if detail:
      detail = IMAGE_RE.sub('', detail)
      detail = '''<html>
<head>
 <style type="text/css">tr.status_failed { background-color:red };</style>
</head>
<body>%s</body>
</html>''' % detail

    # When return fix output for handle unicode issues.
    return detail, sucess_amount, failure_amount, expected_failure_amount, \
        error_title_list

class ERP5TypeFunctionalTestCase(ERP5TypeTestCase):
  run_only = ""
  foreground = 0
  remote_code_url_list = None

  def getTitle(self):
    return "Zelenium"

  def afterSetUp(self):
    super(ERP5TypeFunctionalTestCase, self).afterSetUp()
    # create browser_id_manager
    self.setTimeZoneToUTC()
    if not "browser_id_manager" in self.portal.objectIds():
      self.portal.manage_addProduct['Sessions'].constructBrowserIdManager()
    self.commit()
    self.setSystemPreference()
    self.portal.portal_tests.TestTool_cleanUpTestResults()
    self.tic()
    host, port = self.startZServer()
    self.runner = FunctionalTestRunner(host, port,
                                self.portal, self.run_only)

  def setSystemPreference(self):
    conversion_dict = _getConversionServerDict()
    self.portal.Zuite_setPreference(
       working_copy_list=bt5_dir_list,
       conversion_server_url=conversion_dict['url'],
      )
    # XXX Memcached is missing
    # XXX Persistent cache setup is missing

  def _verboseErrorLog(self, size=10):
    for entry in self.portal.error_log.getLogEntries()[:size]:
      print "="*20
      print "ERROR ID : %s" % entry["id"]
      print "TRACEBACK :"
      print entry["tb_text"]

  def _hasActivityFailure(self):
    """ Return True if the portal has any Activity Failure
    """
    for m in self.portal.portal_activities.getMessageList():
      if m.processing_node < -1:
        return True
    return False

  def testFunctionalTestRunner(self):
    # Check the zuite page templates can be rendered, because selenium test
    # runner does not report error in case there are errors in the page
    # template.
    tests_tool = self.portal.portal_tests

    if self.remote_code_url_list:
      # This does not really run tests. It initializes a zuite
      # and redirect to a url to would actually run them.
      tests_tool.Zuite_runSeleniumTest(self.remote_code_url_list, self.run_only)
      self.commit()

    for page_template_path, page_template in tests_tool.ZopeFind(
        tests_tool[self.run_only] if self.run_only else tests_tool,
        obj_metatypes=('Page Template',), search_sub=1):
      try:
        page_template.pt_render()
      except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.fail('Rendering of %s failed with error:\n%s' % (
          page_template_path,
          ''.join(format_exception(
            exc_type,
            exc_value,
            exc_traceback,
            as_html=False))))

    # abort to get rid of the mysql participation in this transaction
    self.portal._p_jar.sync()

    debug = self.foreground or os.environ.get("erp5_debug_mode")
    error = None
    try:
      self.runner.test(debug=debug)
    except TimeoutError, e:
      error = repr(e)
      self._verboseErrorLog(20)
    else:
      # In case of failure, verbose the error_log entries in order to collect
      # appropriated information to debug the system.
      if self._hasActivityFailure():
        error = 'Failed activities exist.'
        self._verboseErrorLog(20)

    detail, success, failure, \
        expected_failure, error_title_list = self.runner.processResult()

    self.logMessage("-" * 79)
    total = success + failure + expected_failure
    message_args = {"title": self.getTitle(),
                    "total": total,
                    "failure": failure,
                    "expected": expected_failure}
    message = "%(title)s Functional Tests %(total)s Tests, %(failure)s " + \
              "Failures, %(expected)s Expected failures"
    self.logMessage(message % message_args)
    self.logMessage("-" * 79)
    self.logMessage(detail)
    self.logMessage("-" * 79)
    if failure:
      self._verboseErrorLog(20)
    self.assertEqual([], error_title_list, '\n'.join(error_title_list))
    self.assertEqual(None, error, error)

# monkey patch HTTPResponse._unauthorized so that we will not have HTTP
# authentication dialog in case of Unauthorized exception to prevent
# blocking in functional tests.
def _unauthorized(self):
  raise RuntimeError, 'Unauthorized exception happens.'

HTTPResponse._unauthorized = _unauthorized
