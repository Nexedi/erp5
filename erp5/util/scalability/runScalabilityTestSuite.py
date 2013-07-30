#!/usr/bin/env python

import argparse
import os
import time
import sys
import multiprocessing
import subprocess
import signal
import errno
import json
import logging
import logging.handlers
import glob
import urlparse
from erp5.util.benchmark.argument import ArgumentType
from erp5.util.benchmark.performance_tester import PerformanceTester
from erp5.util import taskdistribution
from erp5.util.testnode import Utils


def getConnection(erp5_url):
  parsed = urlparse.urlparse(erp5_url)
  host = "%s:%s" % (parsed.hostname, str(parsed.port))
  if parsed.scheme == 'https':
    return httplib.HTTPSConnection(host)
  elif parsed.scheme == 'http':
    return httplib.HTTPConnection(host)
  else:
    raise ValueError("Protocol not implemented")

MAX_INSTALLATION_TIME = 1200
def waitFor0PendingActivities(erp5_url):
  start_time = time.time()
  while MAX_INSTALLATION_TIME > time.time()-start_time:
    zope_connection = getConnection(erp5_url)
    zope_connection.request(
      'GET', '/erp5/portal_activities/getMessageList',
      headers=header_dict
    )
    result = zope_connection.getresponse()
    message_list_text = result.read()
    message_list = [s.strip() for s in message_list_text[1:-1].split(',')]
    if len(message_list)==0:
      print "There is no pending activities."
      break
    print "There is %d pending activities" %len(message_list)
    time.sleep(5)

    #Hack to do not take into account persistent Alarm_installMailServer acitivities
    if len(message_list)==0 and testIfExist("/erp5/portal_activities", "Alarm_installMailServer"):
      print "1 pending activity for 'Alarm_installMailServer'."
      print "ok."
      break





# XXX: This import is required, just to populate sys.modules['test_suite'].
# Even if it's not used in this file. Yuck.
import product.ERP5Type.tests.ERP5TypeTestSuite


from subprocess import call

LOG_FILE_PREFIX = "performance_tester_erp5"
# Duration of a test case
TEST_CASE_DURATION = 60
# Maximum limit of documents to create during a test case
MAX_DOCUMENTS = 100000

class ScalabilityTest(object):
  def __init__(self, data, test_result):
    self.__dict__ = {}
    self.__dict__.update(data)
    self.test_result = test_result    

def doNothing(**kwargs):
  pass

def makeSuite(test_suite=None, log=doNothing, **kwargs):
  # BBB tests (plural form) is only checked for backward compatibility
  for k in sys.modules.keys():
    if k in ('tests', 'test',) or k.startswith('tests.') or k.startswith('test.'):
      del sys.modules[k]
  singular_succeed = True
  while True:
    module_name, class_name = ('%s.%s' % (singular_succeed and 'test' or 'tests',
                                          test_suite)).rsplit('.', 1)
    try:
      suite_class = getattr(__import__(module_name, None, None, [class_name]),
                            class_name)
    except (AttributeError, ImportError):
      if not singular_succeed:
        raise
      singular_succeed = False
    else:
      break
  suite = suite_class(max_instance_count=1, **kwargs)
  return suite


class ScalabilityLauncher(object):
  def __init__(self):
    # Parse arguments
    self.__argumentNamespace = self._parseArguments(argparse.ArgumentParser(
          description='Run ERP5 benchmarking scalability suites.'))
    # Create Logger
    log_path = os.path.join(self.__argumentNamespace.log_path,
                            "runScalabilityTestSuite.log")
    logger_format = '%(asctime)s %(name)-13s: %(levelname)-8s %(message)s'
    formatter = logging.Formatter(logger_format)
    logging.basicConfig(level=logging.INFO,
                     format=logger_format)
    logger = logging.getLogger('runScalabilityTestSuite')
    logger.addHandler(logging.NullHandler())
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path,
        maxBytes=20000000, backupCount=4)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    self.log = logger.info
    
    # Proxy to with erp5 master test_result
    self.test_result = taskdistribution.TestResultProxyProxy(
                        self.__argumentNamespace.test_suite_master_url,
                        1.0, self.log,
                        self.__argumentNamespace.test_result_path,
                        self.__argumentNamespace.node_title,
                        self.__argumentNamespace.revision
                      )
  @staticmethod
  def _addParserArguments(parser):
    # Mandatory arguments
    parser.add_argument('--erp5-url',
                        metavar='ERP5_URL',
                        help='Main url of ERP5 instance to test')

    parser.add_argument('--test-result-path',
                        metavar='ERP5_TEST_RESULT_PATH',
                        help='ERP5 relative path of the test result')
                             
    parser.add_argument('--revision',
                        metavar='REVISION',
                        help='Revision of the test_suite')
                              
    parser.add_argument('--test-suite',
                        metavar='TEST_SUITE',
                        help='Name of the test suite')
                        
    parser.add_argument('--node-title',
                        metavar='NODE_TITLE',
                        help='Title of the testnode which is running this'
                              'launcher')
                              
    parser.add_argument('--test-suite-master-url',
                        metavar='TEST_SUITE_MASTER_URL',
                        help='Url to connect to the ERP5 Master testsuite taskditributor')
                        
    parser.add_argument('--log-path',
                        metavar='LOG_PATH',
                        help='Log Path')
                        
    parser.add_argument('--erp5-location',
                        metavar='ERP5_LOCATION',
                        help='Path to erp5 depository')
                        
    parser.add_argument('--runner-path',
                        metavar='Runner_PATH',
                        help='runner Path')
   
  @staticmethod
  def _checkParsedArguments(namespace):
    return namespace
    
  @staticmethod
  def _parseArguments(parser):
    ScalabilityLauncher._addParserArguments(parser)
    namespace = parser.parse_args()
    ScalabilityLauncher._checkParsedArguments(namespace)
    return namespace

  def checkERP5Instance(self):
    """
    Check if erp5_instance is accessible
    """
    pass

  def _returnFileContentList(self, path, scheme):
    """
    """
    complete_scheme = os.path.join(path, scheme)
    file_path_list = glob.glob(complete_scheme)
    content_list = []
    for file_path in file_path_list:
      opened_file = open(file_path, 'r')
      content_list.append(''.join(opened_file.readlines()))
      opened_file.close()
    return content_list

  def returnLogList(self):
    return self._returnFileContentList(self.__argumentNamespace.log_path,
                                       "%s*.log" %LOG_FILE_PREFIX)
    
  def returnCsvList(self):
    return self._returnFileContentList(self.__argumentNamespace.log_path,
                                       "%s*.csv" %LOG_FILE_PREFIX)
  def getCreatedDocumentNumber(self):
    number = 0
    complete_scheme = os.path.join(self.__argumentNamespace.log_path,
                                  "%s*.csv" %LOG_FILE_PREFIX)
    file_path_list = glob.glob(complete_scheme)
    for file_path in file_path_list:
      number = number + sum(1 for line in open(file_path))
    return number

  def cleanUpCsv(self):
    files_to_delete = glob.glob(os.path.join(self.__argumentNamespace.log_path,
                                "%s*.csv" %LOG_FILE_PREFIX))
    for file_path in files_to_delete:
      os.remove(file_path)

  def getNextTest(self):
    """
    Return a ScalabilityTest with current running test case informations,
    or None if no test_case ready
    """
    data = self.test_result.getNextTestCase()
    if data == None :
      return None
    decoded_data = Utils.deunicodeData(json.loads(
                  data
                ))
    next_test = ScalabilityTest(decoded_data, self.test_result)
    return next_test

  def getCreatedDocumentNumber(self):
    # First file line is corresponding to header
    number = -1
    complete_scheme = os.path.join(self.__argumentNamespace.log_path,
                                  "%s*.csv" %LOG_FILE_PREFIX)
    file_path_list = glob.glob(complete_scheme)
    for file_path in file_path_list:
      number = number + sum(1 for line in open(file_path))
    return number
    
  def getFailedDocumentNumber(self):
    number = 0
    complete_scheme = os.path.join(self.__argumentNamespace.log_path,
                                  "%s*.csv" %LOG_FILE_PREFIX)
    file_path_list = glob.glob(complete_scheme)
    for file_path in file_path_list:
      opened_file = open(file_path, 'r')
      lines = opened_file.readlines()
      for line in lines:
        if '-1' in line:
          number = number + 1
      opened_file.close()
    return number

  def run(self):
    self.log("Scalability Launcher started, with:")
    self.log("Test suite master url: %s" %self.__argumentNamespace.test_suite_master_url)
    self.log("Test suite: %s" %self.__argumentNamespace.test_suite)
    self.log("Test result path: %s" %self.__argumentNamespace.test_result_path)
    self.log("Revision: %s" %self.__argumentNamespace.revision)
    self.log("Node title: %s" %self.__argumentNamespace.node_title)
    self.log("ERP5 url: %s" %self.__argumentNamespace.erp5_url)
       
    max_time = 36000
    start_time = time.time()
    error_message_set, exit_status = set(), 0

    # Get suite informations
    suite = makeSuite(self.__argumentNamespace.test_suite, self.log)
    test_suites = suite.getTestList()    
    
    while time.time()-start_time < max_time:
      time.sleep(5)
      current_test = self.getNextTest()
      if current_test == None:
        self.log("No Test Case Ready")
      else:
        error_count = 1

        # Waiting for 0-pending activities
        waitFor0PendingActivities(self.__argumentNamespace.erp5_url)

        
        # Here call a runScalabilityTest ( placed on product/ERP5Type/tests ) ?
        self.log("Test Case %s is running..." %(current_test.title))
        try:

          current_test_number = int(current_test.title)
          test_duration = suite.getTestDuration(current_test_number)
          benchmark_path_list = os.path.join(self.__argumentNamespace.erp5_location, suite.getTestPath())
          #TODO: generate a basic user file with all scalability users.
          user_file_path = os.path.join(self.__argumentNamespace.erp5_location, suite.getUsersFilePath())
          tester_path = self.__argumentNamespace.runner_path
          user_number = suite.getUserNumber(current_test_number)

          self.log("user_number: %s" %str(user_number))
          self.log("test_duration: %ss" %str(test_duration))

          #Here: wait for 0-pending activities ?
    
#          tester_process = subprocess.Popen([tester_path,
#                 self.__argumentNamespace.erp5_url,
#                 str(user_number),
#                 ' '.join(test_suites),
#                 '--benchmark-path-list', benchmark_path_list,
#                 '--users-file-path', user_file_path,
#                 '--filename-prefix', "%s_%s_" %(LOG_FILE_PREFIX, current_test.title),
#                 '--report-directory', self.__argumentNamespace.log_path,
#                 '--repeat', "%s" %str(MAX_DOCUMENTS),
#              ])
#          
#          time.sleep(test_duration)
#          tester_process.send_signal(signal.SIGINT)
          error_count = 0
          
        except:
          self.log("Error during tester call.")
          raise ValueError("Tester call failed")
        self.log("Test Case %s is finish" %(current_test.title))

        failed_document_number = self.getFailedDocumentNumber()
        created_document_number = self.getCreatedDocumentNumber() - failed_document_number
        created_document_per_hour_number = ( (float(created_document_number)*60*60) / float(test_duration) )        
        #log_contents = self.returnLogList()
        #csv_contents = self.returnCsvList()
        self.cleanUpCsv()

        retry_time = 2.0
        proxy = taskdistribution.ServerProxy(
                    self.__argumentNamespace.test_suite_master_url,
                    allow_none=True
                ).portal_task_distribution
        test_result_line_test = taskdistribution.TestResultLineProxy(
                                  proxy, retry_time, self.log,
                                  current_test.relative_path,
                                  current_test.title
                                )
                                

        results = "created docs=%d\n"\
                  "failed docs=%d\n"\
                  "duration=%d\n"\
                  "number of tests=%d\n"\
                  %(
                    created_document_number,
                    failed_document_number,
                    test_duration,
                    len(benchmark_path_list)
                  )

        self.log("results:")
        self.log("%s" %results)
        self.log("%s doc in %s secs = %s docs per hour" %(created_document_number, test_duration, created_document_per_hour_number))
#        test_result_line_test.stop(stdout=results,
#                        test_count=created_document_number,
#                        failure_count=failed_document_number,
#                        error_count=error_count,
#                        duration=test_duration)
        self.log("Test Case Stopped")

    return error_message_set, exit_status

def main():
  error_message_set, exit_status = ScalabilityLauncher().run()
  for error_message in error_message_set:
    print >>sys.stderr, "ERROR: %s" % error_message

  sys.exit(exit_status)
