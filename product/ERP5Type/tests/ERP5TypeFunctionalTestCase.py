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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Utils import stopProcess, PR_SET_PDEATHSIG
from lxml import etree
from lxml.html import builder as E
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# selenium workaround for localhost / 127.0.0.1 resolution
# ------
# Selenium connects starts a service on localhost, but when ERP5
# is running under userhosts wrapper, because we don't have entry for
# localhost in our pseudo /etc/hosts file, localhost resolution is delegated
# to local DNS, which might not resolve localhost - for example 8.8.8.8
# does not.
# We work around this by monkey-patching the places in selenium where
# localhost resolution is required and returning 127.0.0.1 directly.
# This is not really correct, it would be better to use SlapOS partition IP,
# but we need a quick fix to have test results again.

# Service.start polls utils.is_connectable(port) - without host argument, assuming the default
# localhost.
# https://github.com/SeleniumHQ/selenium/blob/selenium-3.14.0/py/selenium/webdriver/common/service.py#L99
import selenium.webdriver.common.utils
original_is_connectable = selenium.webdriver.common.utils.is_connectable
def is_connectable(port, host="localhost"):
  if host == "localhost":
    host = "127.0.0.1"
  return original_is_connectable(port, host)
selenium.webdriver.common.utils.is_connectable = is_connectable

# Service.get_service_url hardcodes 127.0.0.1
# https://github.com/SeleniumHQ/selenium/blob/selenium-3.14.0/py/selenium/webdriver/common/service.py#L56
original_join_host_port  = selenium.webdriver.common.utils.join_host_port
def join_host_port(host, port):
  if host == "localhost":
    host = "127.0.0.1"
  return original_join_host_port(host, port)
selenium.webdriver.common.utils.join_host_port = join_host_port
# /selenium workaround


ZELENIUM_BASE_URL = "%s/portal_tests/%s/core/TestRunner.html?test=../test_suite_html&auto=on&resultsUrl=../postResults"

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
      self._runCommand(display_try)
      if self.process.poll() is None:
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

  def _getTestBaseURL(self):
    # Access the https proxy in front of runUnitTest's zserver
    base_url = os.getenv('zserver_frontend_url')
    if base_url:
      return '%s%s' % (base_url, self.portal.getId())
    return self.portal.portal_url()

  def _getTestURL(self):
    return ZELENIUM_BASE_URL % (
        self._getTestBaseURL(),
        self.run_only,
    )

  def test(self, debug=0):
    xvfb = Xvfb(self.instance_home)
    try:
      if not (debug and os.getenv('DISPLAY')):
        print("\nSet 'erp5_debug_mode' environment variable to 1"
              " to use your existing display instead of Xvfb.")
        xvfb.run()
      capabilities = webdriver.common.desired_capabilities \
        .DesiredCapabilities.FIREFOX.copy()
      capabilities['marionette'] = True
      # Zope is accessed through apache with a certificate not trusted by firefox
      capabilities['acceptInsecureCerts'] = True
      # Service workers are disabled on Firefox 52 ESR:
      # https://bugzilla.mozilla.org/show_bug.cgi?id=1338144
      options = webdriver.FirefoxOptions()
      options.set_preference('dom.serviceWorkers.enabled', True)
      kw = dict(capabilities=capabilities, options=options)
      firefox_bin = os.environ.get('firefox_bin')
      if firefox_bin:
        geckodriver = os.path.join(os.path.dirname(firefox_bin), 'geckodriver')
        kw.update(firefox_binary=firefox_bin, executable_path=geckodriver)
      browser = webdriver.Firefox(**kw)
      start_time = time.time()
      browser.get(self._getTestBaseURL() + '/login_form')
      login_field = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, '__ac_name')),
      )
      login_field.clear()
      login_field.send_keys(self.user)
      password_field = browser.find_element_by_name('__ac_password')
      password_field.clear()
      password_field.send_keys(self.password)
      login_form_url = browser.current_url
      password_field.submit()
      WebDriverWait(browser, 10).until(EC.url_changes(login_form_url))
      WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
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
      self.execution_duration = round(time.time() - start_time, 2)
      html_parser = etree.HTMLParser(recover=True)
      iframe = etree.fromstring(
      browser.execute_script(
        "return document.getElementById('testSuiteFrame').contentDocument.querySelector('html').innerHTML"
      ).encode('UTF-8'),
        html_parser
      )
      browser.quit()
    finally:
      xvfb.quit()
    return iframe

  def processResult(self, iframe):
    tbody = iframe.xpath('.//body/table/tbody')[0]
    tr_count = failure_amount = expected_failure_amount = 0
    error_title_list = []
    detail = ""
    for tr in tbody:
      if tr_count:
        # First td is the main title
        test_name = tr[0][0].text
        error = False
        if len(tr) == 1:
          # Test was not executed
          detail += 'Test ' + test_name + ' not executed'
          error_title_list.append(test_name)
        else:
          test_table = tr[1].xpath('.//table')[0]
          status = tr.attrib.get('class')
          if 'status_failed' in status:
            if etree.tostring(test_table).find("expected failure") != -1:
              expected_failure_amount += 1
            else:
              failure_amount += 1
              error_title_list.append(test_name)
            detail_element = E.DIV()
            detail_element.append(E.DIV(E.P(test_name), E.BR, test_table))
            detail += etree.tostring(detail_element)
      tr_count += 1
    sucess_amount = tr_count - 1 - failure_amount - expected_failure_amount
    if detail:
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
    # non-recursive results clean of portal_tests/ or portal_tests/``run_only`` 
    self.portal.portal_tests.TestTool_cleanUpTestResults(self.run_only or None)
    self.tic()
    host, port = self.startZServer()
    self.runner = FunctionalTestRunner(host, port,
                                self.portal, self.run_only)

  def setSystemPreference(self):
    self.portal.Zuite_setPreference(
       working_copy_list=bt5_dir_list,
      )

  def _verboseErrorLog(self, size=10):
    for entry in self.portal.error_log.getLogEntries()[:size]:
      print "="*20
      print "ERROR ID : %s" % entry["id"]
      print "TRACEBACK :"
      print entry["tb_text"]

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
    error = []
    try:
      iframe = self.runner.test(debug=debug)
    except TimeoutError, e:
      error.append(repr(e))
    try:
      self.tic()
    except RuntimeError as e:
      error.append(str(e))

    detail, success, failure, \
        expected_failure, error_title_list = self.runner.processResult(iframe)

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
    if failure or error:
      self._verboseErrorLog(20)
    error += error_title_list
    if error:
      self.fail('\n'.join(error))

# monkey patch HTTPResponse._unauthorized so that we will not have HTTP
# authentication dialog in case of Unauthorized exception to prevent
# blocking in functional tests.
def _unauthorized(self):
  raise RuntimeError, 'Unauthorized exception happens.'

HTTPResponse._unauthorized = _unauthorized
