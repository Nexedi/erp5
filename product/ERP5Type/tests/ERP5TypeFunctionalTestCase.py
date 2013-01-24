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
import sys
import time
import signal
import re
import subprocess
import shutil
import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase, \
                                               _getConversionServerDict

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

class Xvfb:
  def __init__(self, fbdir):
    self.display_list = [":%s" % i for i in range(123, 144)]
    self.display = None
    self.fbdir = fbdir

  def _runCommand(self, display):
    xvfb_bin = os.environ.get("xvfb_bin", "Xvfb")
    with open(os.devnull, 'w') as null:
      self.process = subprocess.Popen(
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
        break
    else:
      raise EnvironmentError("All displays locked : %r" % (self.display_list,))

    print 'Xvfb : %d' % self.process.pid
    print 'Take screenshots using xwud -in %s/Xvfb_screen0' % self.fbdir

  def quit(self):
    if hasattr(self, 'process'):
      self.process.terminate()

class Browser:

  def __init__(self, profile_dir, host, port):
    self.profile_dir = profile_dir
    self.host = host
    self.port = port

  def quit(self):
    if getattr(self, "process", None) is not None:
      self.process.kill()

  def _run(self, url, display):
    """ This method should be implemented on a subclass """
    raise NotImplementedError

  def _setEnviron(self):
    pass

  def run(self, url, display):
    self.clean()
    self._setEnviron()
    self._setDisplay(display)
    self._run(url)
    print "Browser %s running on pid: %s" % (self.__class__.__name__,
                                             self.process.pid)

  def clean(self):
    """ Clean up removing profile dir and recreating it"""
    shutil.rmtree(self.profile_dir, ignore_errors=True)
    os.mkdir(self.profile_dir)

  def _createFile(self, filename, content):
    file_path = os.path.join(self.profile_dir, filename)
    with open(file_path, 'w') as f:
      f.write(content)
    return file_path

  def _setDisplay(self, display):
    if display:
      os.environ["DISPLAY"] = display

  def _runCommand(self, *args):
    print " ".join(args)
    self.process = subprocess.Popen(args, close_fds=True)

class Firefox(Browser):
  """ Use firefox to open run all the tests"""

  def _setEnviron(self):
    os.environ['MOZ_NO_REMOTE'] = '1'
    os.environ['HOME'] = self.profile_dir
    os.environ['LC_ALL'] = 'C'
    os.environ["MOZ_CRASHREPORTER_DISABLE"] = "1"
    os.environ["NO_EM_RESTART"] = "1"

  def _run(self, url):
    # Prepare to run
    self._createFile('prefs.js', self.getPrefJs())
    firefox_bin = os.environ.get("firefox_bin", "firefox")
    self._runCommand(firefox_bin, "-no-remote",
                     "-profile", self.profile_dir, url)

    os.environ['MOZ_NO_REMOTE'] = '0'

  def getPrefJs(self):
    return """
// Don't ask if we want to switch default browsers
user_pref("browser.shell.checkDefaultBrowser", false);

// Disable pop-up blocking
user_pref("browser.allowpopups", true);
user_pref("dom.disable_open_during_load", false);

// Configure us as the local proxy
//user_pref("network.proxy.type", 2);

// Disable security warnings
user_pref("security.warn_submit_insecure", false);
user_pref("security.warn_submit_insecure.show_once", false);
user_pref("security.warn_entering_secure", false);
user_pref("security.warn_entering_secure.show_once", false);
user_pref("security.warn_entering_weak", false);
user_pref("security.warn_entering_weak.show_once", false);
user_pref("security.warn_leaving_secure", false);
user_pref("security.warn_leaving_secure.show_once", false);
user_pref("security.warn_viewing_mixed", false);
user_pref("security.warn_viewing_mixed.show_once", false);

// Disable "do you want to remember this password?"
user_pref("signon.rememberSignons", false);

// increase the timeout before warning of unresponsive script
user_pref("dom.max_script_run_time", 120);

// this is required to upload files
user_pref("capability.principal.codebase.p1.granted", "UniversalFileRead");
user_pref("signed.applets.codebase_principal_support", true);
user_pref("capability.principal.codebase.p1.id", "http://%s:%s");
user_pref("capability.principal.codebase.p1.subjectName", "");

// For debugging, do not waste space on screen
user_pref("browser.tabs.autoHide", true);
""" % (self.host, self.port)

class PhantomJS(Browser):
  def _createRunJS(self):
    run_js = """
var page = new WebPage(),
    address;

address = phantom.args[0];
page.open(address, function (status) {
  if (status !== 'success') {
    console.log('FAIL to load the address');
  } else {
    console.log('SUCCESS load the address');
  }
  phantom.exit();
});
"""
    return self._createFile('run.js', run_js)

  def _run(self, url):
    self._runCommand("phantomjs", self._createRunJS(), url)

class FunctionalTestRunner:

  remote_code_url_list = None

  # There is no test that can take more them 2 hours
  timeout = 2.0 * 60 * 60

  def __init__(self, host, port, portal, run_only='', use_phanthom=False):
    self.instance_home = os.environ['INSTANCE_HOME']

    # Such information should be automatically loaded
    self.user = 'ERP5TypeTestCase'
    self.password = ''
    self.run_only = run_only
    profile_dir = os.path.join(self.instance_home, 'profile')
    self.portal = portal
    if use_phanthom:
      self.browser = PhantomJS(profile_dir, host, int(port))
    else:
      self.browser = Firefox(profile_dir, host, int(port))

  def getStatus(self):
    transaction.begin()
    return self.portal.portal_tests.TestTool_getResults(self.run_only)

  def _getTestURL(self):
    if self.remote_code_url_list is not None:
      remote_code_url = "&".join(["url_list:list=%s" % url for url in self.remote_code_url_list])
      if self.run_only != "":
        remote_code_url += "&zuite_id=%s" % self.run_only
      return '%s/portal_tests/Zuite_runSeleniumTest?%s&__ac_name=%s&__ac_password=%s' \
                 % (self.portal.portal_url(), remote_code_url, self.user, self.password)

    return ZELENIUM_BASE_URL % (self.portal.portal_url(), self.run_only,
                       self.user, self.password)

  def test(self, debug=0):
    try:
      xvfb = Xvfb(self.instance_home)
      start = time.time()
      if not debug:
        print("\nSet 'erp5_debug_mode' environment variable to 1"
              " to use your existing display instead of Xvfb.")
        xvfb.run()
      self.browser.run(self._getTestURL() , xvfb.display)
      while self.getStatus() is None:
        time.sleep(10)
        if (time.time() - start) > float(self.timeout):
          # TODO: here we could take a screenshot and display it in the report
          # (maybe using data: scheme inside a <img>)
          raise TimeoutError("Test took more than %s seconds" % self.timeout)
    except:
      print("ERP5TypeFunctionalTestCase.test Exception: %r" % (sys.exc_info(),))
      raise
    finally:
      xvfb.quit()
      if getattr(self, "browser", None) is not None:
        self.browser.quit()

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
  use_phanthom = False
  remote_code_url_list = None

  def getTitle(self):
    return "Zelenium"

  def afterSetUp(self):
    super(ERP5TypeFunctionalTestCase, self).afterSetUp()
    # create browser_id_manager
    if not "browser_id_manager" in self.portal.objectIds():
      self.portal.manage_addProduct['Sessions'].constructBrowserIdManager()
    self.commit()
    self.setSystemPreference()
    self.portal.portal_tests.TestTool_cleanUpTestResults()
    self.tic()
    self.runner = FunctionalTestRunner(self.serverhost, self.serverport,
                                self.portal, self.run_only, self.use_phanthom)

  def setSystemPreference(self):
    conversion_dict = _getConversionServerDict()
    self.portal.Zuite_setPreference(
       working_copy_list=bt5_dir_list,
       conversion_server_hostname=conversion_dict['hostname'],
       conversion_server_port=conversion_dict['port']
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
    # first of all, abort to get rid of the mysql participation inn this
    # transaction
    self.portal._p_jar.sync()

    if self.remote_code_url_list is not None:
      self.runner.remote_code_url_list = self.remote_code_url_list

    debug = self.foreground or os.environ.get("erp5_debug_mode")
    self.runner.test(debug=debug)
    try:
      detail, success, failure, \
          expected_failure, error_title_list = self.runner.processResult()
    except TimeoutError, e:
      self._verboseErrorLog(20)
      raise

    # In case of failure, verbose the error_log entries in order to collect
    # appropriated information to debug the system.
    if self._hasActivityFailure():
       self._verboseErrorLog(20)

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
    self.assertEquals([], error_title_list, '\n'.join(error_title_list))

