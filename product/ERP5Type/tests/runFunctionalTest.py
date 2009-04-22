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
import pysvn
import atexit

__doc__ = """%(program)s: Zelenium functional test runner for the ERP5 Project

usage: %(program)s [options]

Options:
  -h, --help                 this help screen
  --email_to_address=STRING  send results to this address by email (defaults to
                             erp5-report@erp5.org)
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
Notes:
  * You need to prepepare first test environment by using following command:
  ./runUnitTest.py --save prepareFunctionalTest.py                           
"""


host = 'localhost'
port = 8080
portal_name = 'erp5_portal'
user = 'ERP5TypeTestCase'
password = ''
send_mail = 0
stdout = 0
debug = 0
email_to_address = 'erp5-report@erp5.org'
run_only=''

tests_framework_home = os.path.dirname(os.path.abspath(__file__))
# handle 'system global' instance
if tests_framework_home.startswith('/usr/lib'):
  real_instance_home = '/var/lib/erp5'
else:
  real_instance_home = os.path.sep.join(
    tests_framework_home.split(os.path.sep)[:-3])

instance_home = os.path.join(real_instance_home, 'unit_test')
profile_dir = os.path.join(instance_home, 'profile')
bt5_dir_list = ','.join([
                    os.path.join(instance_home, 'Products/ERP5/bootstrap'),
                    os.path.join(instance_home, 'bt5')])



def usage(stream, msg=None):
  if msg:
    print >>stream, msg
    print >>stream
  program = os.path.basename(sys.argv[0])
  print >>stream, __doc__ % {"program": program}

def parseArgs():
  global send_mail
  global stdout
  global debug
  global email_to_address
  global host
  global port
  global portal_name
  global portal_url
  global run_only
  try:
    opts, args = getopt.getopt(sys.argv[1:],
          "hsd", ["help", "stdout", "debug",
                 "email_to_address=", "host=", "port=", "portal_name=", "run_only="] )
  except getopt.GetoptError, msg:
    usage(sys.stderr, msg)
    sys.exit(2)

  for opt, arg in opts:
    if opt in ("-s", "--stdout"):
      stdout = 1
    elif opt in ("-d", "--debug"):
      debug = 1
    elif opt == '--email_to_address':
      email_to_address = arg
      send_mail = 1
    elif opt in ('-h', '--help'):
      usage(sys.stdout)
      sys.exit()
    elif opt == "--host":
      host = arg
    elif opt == "--port":
      port = int(arg)
    elif opt == "--portal_name":
      portal_name = arg
    elif opt == "--run_only":
      run_only = arg

  if not stdout:
    send_mail = 1

  portal_url = "http://%s:%d/%s" % (host, port, portal_name)

def main():
  setPreference()
  unsubscribeFromTimerService()
  status = getStatus()
  xvfb_pid = None
  firefox_pid = None
  try:
    if not debug:
      xvfb_pid = runXvfb()
    firefox_pid = runFirefox()
    while True:
      sleep(10)
      cur_status = getStatus()
      if status != cur_status:
        break
  finally:
      if xvfb_pid:
        os.kill(xvfb_pid, signal.SIGTERM)
      if firefox_pid:
        os.kill(firefox_pid, signal.SIGTERM)

def startZope():
  os.environ['erp5_force_data_fs'] = "1"
  os.system('%s/bin/zopectl start' % instance_home)
  sleep(2) # ad hoc

def stopZope():
  os.system('%s/bin/zopectl stop' % instance_home)

def runXvfb():
  pid = os.spawnlp(os.P_NOWAIT, 'Xvfb', 'Xvfb', ':123')
  display = os.environ.get('DISPLAY')
  if display:
    auth = Popen(['xauth', 'list', display], stdout=PIPE).communicate()[0]
    if auth:
      (displayname, protocolname, hexkey) = auth.split()
      Popen(['xauth', 'add', 'localhost/unix:123', protocolname, hexkey])
  print 'Xvfb : %d' % pid
  return pid

def prepareFirefox():
  os.system("rm -rf %s" % profile_dir)
  os.mkdir(profile_dir)
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

// this is required to upload files
user_pref("capability.principal.codebase.p1.granted", "UniversalFileRead");
user_pref("signed.applets.codebase_principal_support", true);
user_pref("capability.principal.codebase.p1.id", "http://%s");
user_pref("capability.principal.codebase.p1.subjectName", "");""" % \
    '%s:%s' % (host, port)
  pref_file = open(os.path.join(profile_dir, 'prefs.js'), 'w')
  pref_file.write(prefs_js)
  pref_file.close()

def runFirefox():
  prepareFirefox()
  if debug:
    try:
      shutil.copy2(os.path.expanduser('~/.Xauthority'), '%s/.Xauthority' % profile_dir)
    except IOError:
      pass
  else:
    os.environ['DISPLAY'] = ':123'
  os.environ['MOZ_NO_REMOTE'] = '1'
  os.environ['HOME'] = profile_dir
  # check if old zelenium or new zelenium
  try:
    urllib2.urlopen("%s/portal_tests/core/scripts/selenium-version.js" % portal_url)
  except urllib2.HTTPError:
    # Zelenium 0.8
    url_string = "%s/portal_tests/?auto=true&__ac_name=%s&__ac_password=%s" % (portal_url, user, password)
  else:
    # Zelenium 0.8+ or later
    url_string = "%s/portal_tests/core/TestRunner.html?test=../test_suite_html&auto=on&resultsUrl=%s/portal_tests/postResults&__ac_name=%s&__ac_password=%s" % (portal_url, portal_url, user, password)
  if run_only:
    url_string = url_string.replace('/portal_tests/', '/portal_tests/%s/' % run_only, 1)
  pid = os.spawnlp(os.P_NOWAIT, "firefox", "firefox", "-profile", profile_dir,
      url_string)
  os.environ['MOZ_NO_REMOTE'] = '0'
  print 'firefox : %d' % pid
  return pid

def getStatus():
  try:
    status = urllib2.urlopen('%s/portal_tests/TestTool_getResults'
                             % portal_url).read()
  except urllib2.HTTPError, e:
    if e.msg == "No Content" :
      status = ""
    else:
      raise
  return status

def setPreference():
  urllib2.urlopen('%s/BTZuite_setPreference?__ac_name='
                  '%s&__ac_password=%s&working_copy_list=%s' %
                  (portal_url, user, password, bt5_dir_list))

def unsubscribeFromTimerService():
  urllib2.urlopen('%s/portal_activities/?unsubscribe:method='
                  '&__ac_name=%s&__ac_password=%s' %
                  (portal_url, user, password))

def sendResult():
  result_uri = urllib2.urlopen('%s/portal_tests/TestTool_getResults' % portal_url).readline()
  print result_uri
  file_content = urllib2.urlopen(result_uri).read()
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
  os.chdir('%s/Products/ERP5' % instance_home)
  revision = pysvn.Client().info('.').revision.number

  subject = "ERP5 r%s: Functional Tests, %s Passes, %s Failures" \
                                          % (revision, passes, failures)
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
  detail = detail.replace('<tr class="title status_failed"', '<tr class="title status_failed" style="background-color:red"')
  detail = detail.replace('<tr class="status_failed"', '<tr class="status_failed" style="background-color:red"')
  if detail:
    detail = '<html><body>%s</body></html>' % detail
  status = (not failures)
  if send_mail:
    sendMail(subject=subject,
             body=summary,
             status=status,
             attachments=[detail],
             from_mail='nobody@svn.erp5.org',
             to_mail=[email_to_address])
  if stdout:
    print '-' * 79
    print subject
    print '-' * 79
    print summary
    print '-' * 79
    print detail
  return int(failures)

if __name__ == "__main__":
  parseArgs()
  startZope()
  atexit.register(stopZope)
  main()
  sys.exit(sendResult())

