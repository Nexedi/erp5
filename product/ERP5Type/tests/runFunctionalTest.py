#!/usr/bin/env python2.4
import os
import re
import signal
import sys
import shutil
import getopt
from time import sleep
import urllib2
from subprocess import Popen, PIPE
from sendMail import sendMail
import atexit

__doc__ = """%(program)s: Zelenium functional test runner for the ERP5 Project

usage: %(program)s [options]

Options:
  -h, --help                 this help screen
  --email_to_address=STRING  send results to this address by email (defaults to
                             erp5-report@erp5.org)
  --smtp_host=hostname       specify SMTP server
  -s, --stdout               print the results on stdout instead of sending
                             results by email (unless email_to_address is also
                             passed explictly)
  -d, --debug                run firefox on current DISPLAY instead of on Xvfb
  --host                     the hostname of this ERP5 instance
  --port                     the port of this ERP5 instance
  --portal_name              the ID of the ERP5 site
                             URLs will start with:
                                 http://${host}:${port}/${portal_name}/
  --run_only=STRING          run only specified test suite (should be only one)
  --email_subject            the email subject to be sent
  --xvfb_display=STRING      Define a xvfb display to be used.
Notes:
  * You need to prepepare first test environment by using following command:
  ./runUnitTest.py --save prepareFunctionalTest.py
"""

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

class FunctionalTestRunner:
  """
    Used to run Functional tests
  """
  def __init__(self, instance_home):
    self.instance_home = instance_home
    self.xvfb_fbdir = instance_home
    self.send_mail = 0
    self.stdout = 0
    self.debug = 0
    self.email_to_address = 'erp5-report@erp5.org'
    self.smtp_host = ''
    self.host = 'localhost'
    self.port = 8080
    self.user = 'ERP5TypeTestCase'
    self.password = ''
    self.portal_name = 'erp5_portal'
    self.run_only = ''
    self.email_subject = 'ERP5'
    self.xvfb_display = '123'
    self.profile_dir = os.path.join(instance_home, 'profile')

  def usage(self, stream, msg=None):
    if msg:
      print >>stream, msg
      print >>stream
    program = os.path.basename(sys.argv[0])
    print >>stream, __doc__ % {"program": program}

  def parseArgs(self, arguments=None):
    if arguments is None:
      arguments = sys.argv[1:]
    try:
      opts, args = getopt.getopt(arguments,
            "hsd", ["help", "stdout", "debug",
                   "email_to_address=", "host=", "port=",
                   "portal_name=", "run_only=", "user=",
                   "password=", "alarms=",
                   "email_subject=", "smtp_host=", "xvfb_display="] )
    except getopt.GetoptError, msg:
      self.usage(sys.stderr, msg)
      sys.exit(2)
  
    for opt, arg in opts:
      if opt in ("-s", "--stdout"):
        self.stdout = 1
      elif opt in ("-d", "--debug"):
        self.debug = 1
      elif opt == '--email_to_address':
        self.email_to_address = arg
        self.send_mail = 1
      elif opt == '--smtp_host':
        self.smtp_host = arg
      elif opt in ('-h', '--help'):
        self.usage(sys.stdout)
        sys.exit()
      elif opt == "--host":
        self.host = arg
      elif opt == "--port":
        self.port = int(arg)
      elif opt == "--portal_name":
        self.portal_name = arg
      elif opt == "--run_only":
        self.run_only = arg
      elif opt == "--user":
        user = arg
      elif opt == "--password":
        password = arg
      elif opt == "--email_subject":
        self.email_subject = arg
      elif opt == "--xvfb_display":
        self.xvfb_display = arg
  
    if not self.stdout:
      self.send_mail = 1
  
    self.portal_url = "http://%s:%d/%s" % (self.host, self.port, self.portal_name)
  
  def openUrl(self, url):
    # Send Accept-Charset headers to activate the UnicodeConflictResolver
    # (imitating firefox 3.5.9 here)
    headers = { 'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.7' }
    request = urllib2.Request(url, headers=headers)
    # Try to use long timeout, this is needed when there is many
    # activities runing
    try:
      f = urllib2.urlopen(request, timeout=3600)
    except TypeError:
      f = urllib2.urlopen(request)
    file_content = f.read()
    f.close()
    return file_content
  
  def main(self):
    self.setUp()
    self.launchFuntionalTest()

  def launchFuntionalTest(self):
    status = self.getStatus()
    xvfb_pid = None
    firefox_pid = None
    try:
      if not self.debug:
        xvfb_pid = self.runXvfb(self.xvfb_display)
      firefox_pid = self.runFirefox(self.xvfb_display)
      while True:
        sleep(10)
        cur_status = self.getStatus()
        if status != cur_status:
          break
    finally:
        if xvfb_pid:
          os.kill(xvfb_pid, signal.SIGTERM)
        if firefox_pid:
          os.kill(firefox_pid, signal.SIGTERM)
  
  def startZope(self):
    os.environ['erp5_save_data_fs'] = "1"
    os.system('%s/bin/zopectl start' % self.instance_home)
    sleep(2) # ad hoc
  
  def stopZope(self):
    os.system('%s/bin/zopectl stop' % self.instance_home)
  
  def runXvfb(self, xvfb_display):
    pid = os.spawnlp(os.P_NOWAIT, 'Xvfb', 'Xvfb',
                     '-fbdir' , '%s' % self.xvfb_fbdir  ,
                     ':%s' % xvfb_display)
    display = os.environ.get('DISPLAY')
    if display:
      auth = Popen(['xauth', 'list', display], stdout=PIPE).communicate()[0]
      if auth:
        (displayname, protocolname, hexkey) = auth.split()
        Popen(['xauth', 'add', 'localhost/unix:%s' %xvfb_display, protocolname, hexkey])
    print 'Xvfb : %d' % pid
    print 'Take screenshots using xwud -in %s/Xvfb_screen0' % self.xvfb_fbdir
    return pid

  def getPrefJs(self, host, port):
    prefs_js = """
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
user_pref("capability.principal.codebase.p1.id", "http://%s");
user_pref("capability.principal.codebase.p1.subjectName", "");""" % \
      '%s:%s' % (host, port)
    return prefs_js

  def prepareFirefox(self, prefs_js=''):
    os.system("rm -rf %s" % self.profile_dir)
    os.mkdir(self.profile_dir)
    pref_file = open(os.path.join(self.profile_dir, 'prefs.js'), 'w')
    pref_file.write(prefs_js)
    pref_file.close()
  
  def runFirefox(self,xvfb_display):
    prefs_js = self.getPrefJs(self.host, self.port)
    self.prepareFirefox(prefs_js)
    if self.debug:
      try:
        shutil.copy2(os.path.expanduser('~/.Xauthority'), '%s/.Xauthority' % self.profile_dir)
      except IOError:
        pass
    else:
      os.environ['DISPLAY'] = ':%s' %xvfb_display
    os.environ['MOZ_NO_REMOTE'] = '1'
    os.environ['HOME'] = self.profile_dir
    os.environ['LC_ALL'] = 'C'
    # check if old zelenium or new zelenium
    try:
      urllib2.urlopen("%s/portal_tests/core/scripts/selenium-version.js" % self.portal_url)
    except urllib2.HTTPError:
      # Zelenium 0.8
      url_string = "%s/portal_tests/?auto=true&__ac_name=%s&__ac_password=%s" % (self.portal_url, self.user, self.password)
    else:
      # Zelenium 0.8+ or later
      url_string = "%s/portal_tests/core/TestRunner.html?test=../test_suite_html&auto=on&resultsUrl=%s/portal_tests/postResults&__ac_name=%s&__ac_password=%s" % (self.portal_url, self.portal_url, self.user, self.password)
  
    if self.run_only:
      url_string = url_string.replace('/portal_tests/', '/portal_tests/%s/' % self.run_only, 1)
    pid = os.spawnlp(os.P_NOWAIT, "firefox", "firefox",
        "-no-remote", "-profile", self.profile_dir,
        url_string)
    os.environ['MOZ_NO_REMOTE'] = '0'
    print 'firefox : %d' % pid
    return pid
  
  def getStatus(self):
    try:
      status = self.openUrl('%s/portal_tests/TestTool_getResults'
                               % (self.portal_url))
    except urllib2.HTTPError, e:
      if e.msg == "No Content" :
        status = ""
      else:
        raise
    return status
  
  def setPreference(self):
    conversion_server_hostname = os.environ.get('conversion_server_hostname',
                                                'localhost')
    conversion_server_port = os.environ.get('conversion_server_port', '8008')
    urllib2.urlopen('%s/Zuite_setPreference?__ac_name='
                    '%s&__ac_password=%s&working_copy_list=%s'
                    '&conversion_server_hostname=%s'
                    '&conversion_server_port=%s'%
                    (self.portal_url, self.user, self.password,
                      bt5_dir_list, conversion_server_hostname,
                      conversion_server_port))
  

  def unsubscribeFromTimerService(self):
    urllib2.urlopen('%s/portal_activities/?unsubscribe:method='
                    '&__ac_name=%s&__ac_password=%s' %
                    (self.portal_url, self.user, self.password))

  def setUp(self):
    self.setPreference()
    self.unsubscribeFromTimerService()

  def getSvnRevision(self):
    """Get svn revision used."""
    import pysvn
    return pysvn.Client().info(os.path.dirname(__file__)).revision.number

  def sendResult(self):
    file_content = self.openUrl('%s/portal_tests/TestTool_getResults' % self.portal_url)
    passes_re = re.compile('<th[^>]*>Tests passed</th>\n\s*<td[^>]*>([^<]*)')
    failures_re = re.compile('<th[^>]*>Tests failed</th>\n\s*<td[^>]*>([^<]*)')
    image_re = re.compile('<img[^>]*?>')
    error_title_re = re.compile('(?:error.gif.*?>|title status_failed"><td[^>]*>)([^>]*?)</td></tr>', re.S)
    result_re = re.compile('<div style="padding-top: 10px;">\s*<p>\s*'
                          '<img.*?</div>\s.*?</div>\s*', re.S)
    error_result_re = re.compile('.*(?:error.gif|title status_failed).*', re.S)
    passes = passes_re.search(file_content).group(1)
    failures = failures_re.search(file_content).group(1)
    error_titles = [re.compile('\s+').sub(' ', x).strip()
                    for x in error_title_re.findall(file_content)]
    revision = self.getSvnRevision()
  
    subject = "%s r%s: Functional Tests, %s Passes, %s Failures" \
                % (self.email_subject, revision, passes, failures)
    summary = """
Test Summary

Tests passed: %4s
Tests failed: %4s

Following tests failed:

%s""" % (passes, failures, "\n".join(error_titles))
    detail = ''
    for e in result_re.findall(file_content):
      if error_result_re.match(e):
        detail += e
    detail = image_re.sub('', detail)
    if detail:
      detail = '''<html>
<head>
 <style type="text/css">tr.status_failed { background-color:red };</style>
</head>
<body>%s</body>
</html>''' % detail
    status = (not failures)
    if self.send_mail:
      sendMail(subject=subject,
               body=summary,
               status=status,
               attachments=[detail],
               from_mail='nobody@svn.erp5.org',
               to_mail=[self.email_to_address],
               smtp_host=self.smtp_host)
    if self.stdout:
      print '-' * 79
      print subject
      print '-' * 79
      print summary
      print '-' * 79
      print detail
    return int(failures)

if __name__ == "__main__":
  test_runner = FunctionalTestRunner(instance_home)
  test_runner.parseArgs()
  test_runner.startZope()
  atexit.register(test_runner.stopZope)
  test_runner.main()
  sys.exit(test_runner.sendResult())
