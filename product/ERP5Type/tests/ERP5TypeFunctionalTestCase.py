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
import transaction
from time import sleep
import signal
import re
from subprocess import Popen, PIPE
import shutil

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

ZELENIUM_BASE_URL = "%s/portal_tests/%s/core/TestRunner.html?test=../test_suite_html&auto=on&resultsUrl=%s/portal_tests/postResults&__ac_name=%s&__ac_password=%s"

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

class Xvfb:
  def __init__(self, fbdir, display):
    self.display = display
    self.fbdir = fbdir
    self.pid = None

  def run(self):
    self.pid = os.spawnlp(os.P_NOWAIT, 'Xvfb', 'Xvfb',
                          '-fbdir' , self.fbdir, self.display)

    display = os.environ.get('DISPLAY')
    if display:
      auth = Popen(['xauth', 'list', display], stdout=PIPE).communicate()[0]
      if auth:
        (displayname, protocolname, hexkey) = auth.split()
        Popen(['xauth', 'add', 'localhost/unix:%s' % display, protocolname, hexkey])

    print 'Xvfb : %d' % self.pid
    print 'Take screenshots using xwud -in %s/Xvfb_screen0' % self.fbdir

  def quit(self):
    if self.pid:
      print "Stopping Xvfb on pid: %s" % self.pid
      os.kill(self.pid, signal.SIGTERM)

class Firefox:
  
  def __init__(self, profile_dir, host, port):
    self.profile_dir = profile_dir
    self.host = host
    self.port = port
    self.pid = None

  def quit(self):
    if self.pid:
      os.kill(self.pid, signal.SIGTERM)

  def run(self, url, display):
    self._prepare()
    
    if display is None:
      try:
        shutil.copy2(os.path.expanduser('~/.Xauthority'), '%s/.Xauthority' % self.profile_dir)
      except IOError:
        pass
    else:
      os.environ["DISPLAY"] = display

    os.environ['MOZ_NO_REMOTE'] = '1'
    os.environ['HOME'] = self.profile_dir
    os.environ['LC_ALL'] = 'C'
    os.environ["MOZ_CRASHREPORTER_DISABLE"] = "1"
    os.environ["NO_EM_RESTART"] = "1"

    command_tuple = ("firefox", "firefox",  "-no-remote",
                 "-profile", self.profile_dir, url)

    print " ".join(list(command_tuple))

    self.pid = os.spawnlp(os.P_NOWAIT, *command_tuple)
    os.environ['MOZ_NO_REMOTE'] = '0'
    print 'firefox : %d' % self.pid
    return self.pid

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
user_pref("capability.principal.codebase.p1.subjectName", "");""" % \

  def _prepare(self):
    prefs_js = self.getPrefJs(self.host, self.port)
    os.system("rm -rf %s" % self.profile_dir)
    os.mkdir(self.profile_dir)
    pref_file = open(os.path.join(self.profile_dir, 'prefs.js'), 'w')
    pref_file.write(prefs_js)
    pref_file.close()

  def isXvfbRequired(self):
    return True


class FunctionalTestRunner:


  
  def __init__(self, host, port, portal, run_only=''):
    self.instance_home = os.environ['INSTANCE_HOME']
    self.host = host
    self.port = int(port)
    # Such informations should be automatically loaded
    self.user = 'ERP5TypeTestCase'
    self.password = ''
    self.run_only = run_only
    self.xvfb_display = ':123'
    self.profile_dir = os.path.join(self.instance_home, 'profile')
    self.portal_url = "http://%s:%d/%s" % (host, port, portal.getId())
    self.portal = portal


  def getStatus(self):
    transaction.commit()
    return self.portal.portal_tests.TestTool_getResults()

  def _getTestURL(self):
    return ZELENIUM_BASE_URL % (self.portal.portal_url(), self.run_only,
                      self.portal.portal_url(), self.user, self.password)

  def launchFunctionalTest(self, debug=0):
    pid = None
    test_url = self._getTestURL(self.run_only)
    browser = Firefox(self.profile_dir, self.host, self.port)
    display = None
    xvfb = Xvfb(self.instance_home, None)
    try:
      if not debug and browser.isXvfbRequired():
        xvfb.display = self.xvfb_display
        xvfb.run()
      browser.run(test_url, xvfb.display)
      while self.getStatus() is None:
        sleep(10)

    finally:
      browser.quit()
      xvfb.quit()

  def processResult(self):
    file_content = self.getStatus()
    sucess_amount = TEST_PASS_RE.search(file_content).group(1)
    failure_amount = TEST_FAILURE_RE.search(file_content).group(1)
    error_title_list = [re.compile('\s+').sub(' ', x).strip()
                    for x in TEST_ERROR_TITLE_RE.findall(file_content)]

    detail = ''
    for test_result in TEST_RESULT_RE.findall(file_content):
      if  TEST_ERROR_RESULT_RE.match(test_result):
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

    return detail, int(sucess_amount), int(failure_amount), error_title_list



class ERP5TypeFunctionalTestCase(ERP5TypeTestCase):

  run_only = ""
  foreground = 0

  def getTitle(self):
    return "Zelenium"

  def afterSetUp(self):
    # create browser_id_manager
    if not "browser_id_manager" in self.portal.objectIds():
      self.portal.manage_addProduct['Sessions'].constructBrowserIdManager()
    transaction.commit()
    self.setSystemPreference()
    self.portal.portal_tests.TestTool_cleanUpTestResults()
    self.stepTic()

  def setSystemPreference(self):
    conversion_dict = _getConversionServerDict()
    self.portal.Zuite_setPreference(
       working_copy_list=bt5_dir_list,
       conversion_server_hostname=conversion_dict['hostname'],
       conversion_server_port=conversion_dict['port']
      )
    # XXX Memcached is missing
    # XXX Persistent cache setup is missing

  def testFunctionalTestRunner(self):
    # first of all, abort to get rid of the mysql participation inn this
    # transaction
    self.portal._p_jar.sync()
    self.runner = FunctionalTestRunner(self.serverhost, self.serverport, 
                                       self.portal, self.run_only)
    self.runner.launchFunctionalTest(debug=self.foreground)

    detail, success, failure, error_title_list = self.runner.processResult()

    self.logMessage("-" * 79)
    total = success + failure
    self.logMessage("%s Functional Tests %s Tests, %s Failures" % \
                    (self.getTitle(), total, failure))
    self.logMessage("-" * 79)
    self.logMessage(detail)
    self.logMessage("-" * 79)
    self.assertEquals([], error_title_list)
