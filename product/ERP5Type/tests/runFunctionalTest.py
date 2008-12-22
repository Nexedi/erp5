#!/usr/bin/env python2.4
import os
import re
import signal
import sys
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
  -s, --stdout               prints the results on stdout instead of sending
                             results by email (unless email_to_address is also
                             passed explictly)
  --host                     the hostname of this ERP5 instance
  --port                     the port of this ERP5 instance
  --portal_name              the ID of the ERP5 site
                             URLs will start with:
                                 http://${host}:${port}/${portal_name}/
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
email_to_address = 'erp5-report@erp5.org'

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
  global email_to_address
  global host
  global port
  global portal_name
  try:
    opts, args = getopt.getopt(sys.argv[1:],
          "hs", ["help", "stdout",
                 "email_to_address=", "host=", "port=", "portal_name="] )
  except getopt.GetoptError, msg:
    usage(sys.stderr, msg)
    sys.exit(2)
  
  for opt, arg in opts:
    if opt in ("-s", "--stdout"):
      stdout = 1
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

  if not stdout:
    send_mail = 1

def main():
  setBaseUrl()
  setPreference()
  unsubscribeFromTimerService()
  status = getStatus()
  xvfb_pid = None
  firefox_pid = None
  try:
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
  os.environ['MOZ_NO_REMOTE'] = '1'
  os.environ['DISPLAY'] = ':123'
  os.environ['HOME'] = profile_dir
  prepareFirefox()
  pid = os.spawnlp(os.P_NOWAIT, "firefox", "firefox", "-profile", profile_dir,
      "http://%s:%d/%s/portal_tests/?auto=true&__ac_name=%s"
          "&__ac_password=%s" % (host, port, portal_name, user, password))
  os.environ['MOZ_NO_REMOTE'] = '0'
  print 'firefox : %d' % pid
  return pid

def getStatus():
  try:
    status = urllib2.urlopen('http://%s:%d/%s/TestTool_getResults'
                                % (host, port, portal_name)).read()
  except urllib2.HTTPError, e:
    if e.msg == "No Content" :
      status = ""
    else:
      raise
  return status

def setPreference():
  urllib2.urlopen('http://%s:%d/%s/BTZuite_setPreference?__ac_name='
              '%s&__ac_password=%s&working_copy_list=%s' %
                                  (host, port, portal_name, user, password, bt5_dir_list))

def setBaseUrl():
  urllib2.urlopen('http://%s:%d/%s/Zuite_setBaseUrl?__ac_name='
              '%s&__ac_password=%s&base_url=%s' %
                                  (host, port, portal_name, user, password, portal_name))

def unsubscribeFromTimerService():
  urllib2.urlopen('http://%s:%d/%s/portal_activities/?unsubscribe:method='
                  '&__ac_name=%s&__ac_password=%s' %
                                  (host, port, portal_name, user, password))

def sendResult():
  result_uri = urllib2.urlopen('http://%s:%d/%s/TestTool_getResults' %
                                    (host, port, portal_name)).readline()
  file_content = urllib2.urlopen(result_uri).read()
  passes_re = re.compile('<th[^>]*>Tests passed</th>\n\s*<td[^>]*>([^<]*)')
  failures_re = re.compile('<th[^>]*>Tests failed</th>\n\s*<td[^>]*>([^<]*)')
  check_re = re.compile('<img[^>]*?/check.gif"\s*[^>]*?>')
  error_re = re.compile('<img[^>]*?/error.gif"\s*[^>]*?>')
  error_title_re = re.compile('error.gif.*?>([^>]*?)</td></tr>', re.S)
  pass_test_re = re.compile('<div style="padding-top: 10px;">\s*<p>\s*'
                        '<img[^>]*?/check.gif".*?</div>\s.*?</div>\s*', re.S)
  footer_re = re.compile('<h2> Remote Client Data </h2>.*</table>', re.S)

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
  file_content = pass_test_re.sub('', file_content)
  file_content = footer_re.sub('', file_content)
  file_content = check_re.sub(
                      '<span style="color: green">PASS</span>', file_content)
  file_content = error_re.sub(
                      '<span style="color: red">FAIL</span>', file_content)
  status = (not failures)
  if send_mail:
    sendMail(subject=subject,
             body=summary,
             status=status,
             attachments=[file_content],
             from_mail='nobody@svn.erp5.org',
             to_mail=[email_to_address])
  if stdout:
    print '-' * 79
    print subject
    print '-' * 79
    print summary
    print '-' * 79
    print file_content
  return int(failures)

if __name__ == "__main__":
  parseArgs()
  startZope()
  atexit.register(stopZope)
  main()
  sys.exit(sendResult())

