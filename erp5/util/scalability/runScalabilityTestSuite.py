#!/usr/bin/env python

import argparse
import os
import shutil
import time
import sys
import multiprocessing
import subprocess
from subprocess import call
import signal
import errno
import json
import logging
import traceback
import logging.handlers
import glob
import urlparse
import httplib
import base64
import requests
from erp5.util.benchmark.argument import ArgumentType
from erp5.util.benchmark.performance_tester import PerformanceTester
from erp5.util import taskdistribution
from erp5.util.testnode import Utils
import datetime

MAX_INSTALLATION_TIME = 60*50
MAX_TESTING_TIME = 60
MAX_GETTING_CONNECTION_TIME = 60*5

SCALABILITY_LOG_FILENAME = "runScalabilityTestSuite.log"
LOG_FILE_PREFIX = "scalability-test"
# Duration of a test case
TEST_CASE_DURATION = 60
# Maximum limit of documents to create during a test case
MAX_DOCUMENTS = 1
MAX_ERRORS = 1

class DummyLogger(object):
  def __init__(self, func):
    for name in ('trace', 'debug', 'info', 'warn', 'warning', 'error',
      'critical', 'fatal'):
       setattr(self, name, func)

def getConnection(erp5_url, log):
  """
  Return a connection with the erp5 instance.
  """
  start_time = time.time()
  count = 0
  while MAX_GETTING_CONNECTION_TIME > time.time()-start_time:
    try:
      count = count + 1
      parsed = urlparse.urlparse(erp5_url)
      host = "%s:%s" % (parsed.hostname, str(parsed.port))
      if parsed.scheme == 'https':
        return httplib.HTTPSConnection(host)
      elif parsed.scheme == 'http':
        return httplib.HTTPConnection(host)
      else:
        raise ValueError("Protocol not implemented")
    except:
      log("Can't get connection to %s, we will retry." %erp5_url)
      time.sleep(10)
  raise ValueError("Cannot get new connection after %d try (for %s s)" %(count, str(time.time()-start_time)))

def waitFor0PendingActivities(erp5_url, log):
  """
  Waiting while there are no pending activities on the erp5 instance.
  """
  start_time = time.time()
  parsed = urlparse.urlparse(erp5_url)
  user = parsed.username;
  password = parsed.password;
  header_dict = {'Authorization': 'Basic %s' % \
  base64.encodestring('%s:%s' % (user, password)).strip()}

  count = 0
  ok = False
  while MAX_INSTALLATION_TIME > time.time()-start_time and not ok:
    zope_connection = getConnection(erp5_url, log)
    try:
      count = count + 1
      zope_connection.request(
        'GET', '/erp5/portal_activities/getMessageList',
        headers=header_dict
      )
      result = zope_connection.getresponse()
      message_list_text = result.read()
      message_list = [s.strip() for s in message_list_text[1:-1].split(',')]
      if len(message_list)==0:
        log("There is no pending activities.")
        ok = True
      #Hack to do not take into account persistent Alarm_installMailServer acitivities
      if len(message_list)==1 :
        log("1 pending activity but ok.")
        ok = True

      log("There is %d pending activities" %len(message_list))
      time.sleep(5)
    except:
      time.sleep(5)
      log("Getting activities failed, retry.")

  if not ok:
    raise ValueError("Cannot waitFor0PendingActivities after %d try (for %s s)" %(count, str(time.time()-start_time)))

def getCreatedDocumentNumberFromERP5(erp5_url, log):
  """
  Get the number of created documents from erp5 instance.
  """
  log("count docs number from ERP5 instance")
  count_retry = 0
  parsed = urlparse.urlparse(erp5_url)
  user = 'zope'
  password = 'insecure'
  header_dict = {'Authorization': 'Basic %s' % \
  base64.encodestring('%s:%s' % (user, password)).strip()}
  zope_connection = getConnection(erp5_url, log)
  while count_retry < 100 :
    try:
      zope_connection.request(
        'GET', '/erp5/count_docs_scalability',
        headers=header_dict
      )
      result = zope_connection.getresponse()
      return int(result.read())
    except:
      log("retry..")
      count_retry += 1
      time.sleep(15)
  raise ValueError("Impossible to get number of docs from ERP5")

class ScalabilityTest(object):
  def __init__(self, data, test_result):
    self.__dict__ = {}
    self.__dict__.update(data)
    self.test_result = test_result

def doNothing(**kwargs):
  pass

def makeSuite(test_suite=None, location=None, log=doNothing, **kwargs):
  import imp
  try:
    module = imp.load_source('scalability_test', location + '__init__.py')
    suite_class = getattr(module, test_suite)
    suite = suite_class(**kwargs)
  except (AttributeError, ImportError) as e:
    log("[ERROR] AttributeError or ImportError while making suite")
    log(traceback.format_exc())
    raise BaseException("AttributeError or ImportError while making suite: " + str(e))
  except Exception as e:
    log("[ERROR] While making suite: ")
    log(traceback.format_exc())
    raise
  return suite
 
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
    log_path = os.path.join(self.__argumentNamespace.log_path, SCALABILITY_LOG_FILENAME)
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
    self.logger = logger
    self.users_file_original_content = []

    portal_url = self.__argumentNamespace.test_suite_master_url
    distributor = taskdistribution.TaskDistributor(portal_url, logger=DummyLogger(self.log))

    # Proxy to with erp5 master test_result
    self.log(self.__argumentNamespace.test_suite_master_url)
    self.test_result = taskdistribution.TestResultProxy(
                        distributor,
                        1.0, DummyLogger(self.log),
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

    parser.add_argument('--erp5-user',
                        metavar='ERP5_USER',
                        help='Main user of ERP5 instance to test')

    parser.add_argument('--erp5-password',
                        metavar='ERP5_PASSWORD',
                        help='Main password of ERP5 instance to test')

    parser.add_argument('--test-result-path',
                        metavar='ERP5_TEST_RESULT_PATH',
                        help='ERP5 relative path of the test result')

    parser.add_argument('--revision',
                        metavar='REVISION',
                        help='Revision of the test_suite')

    parser.add_argument('--current-test-data',
                        metavar='CURRENT_TEST_DATA',
                        help='Data of the current test')

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

  def moveLogs(self, folder_name):
    # Get file paths
    file_to_move_list = glob.glob(os.path.join(self.__argumentNamespace.log_path,
                                "%s*.csv" %LOG_FILE_PREFIX))
    file_to_move_list += glob.glob(os.path.join(self.__argumentNamespace.log_path,
                                "%s*.log" %LOG_FILE_PREFIX))
    # Create folder
    new_directory_path = os.path.join(self.__argumentNamespace.log_path,
                                folder_name)
    if not os.path.exists(new_directory_path):
      os.makedirs(new_directory_path)
    # Move files
    for file_to_move in file_to_move_list:
      shutil.move(file_to_move, new_directory_path)

  def getRunningTest(self):
    """
    Return a ScalabilityTest with current running test case informations
    """
    data_array = self.__argumentNamespace.current_test_data.split(',')
    data = json.dumps({"count": data_array[0], "title": data_array[1], "relative_path": data_array[2]})
    decoded_data = Utils.deunicodeData(json.loads(data))
    return ScalabilityTest(decoded_data, self.test_result)

  def createScalabilityUsersInInstance(self, user_quantity):
    # GET request to script for user creation
    self.log("Creating users")
    erp5_url = "http://%s:%s@%s/erp5" % (self.__argumentNamespace.erp5_user,
                                         self.__argumentNamespace.erp5_password,
                                         self.__argumentNamespace.erp5_url)
    try:
      response = requests.get(erp5_url + '/ERP5Site_createScalabilityTestUsers?user_quantity=%i' % user_quantity)
    except Exception as e:
      raise BaseException("While creating users: " + str(e))
    if response.status_code == 200:
      try:
        response_dict = eval(response.text)
      except:
        raise BaseException("While creating users: dictionary response expected.")
      if response_dict["status_code"] == 0:
        return response_dict["password"]
      else:
        raise BaseException("While creating users: " + response_dict["error_message"])
    else:
      raise BaseException("While creating users: response status " + str(response.status_code))

  def clearUsersFile(self, user_file_path):
    self.log("Clearing users file: %s" % user_file_path)
    os.remove(user_file_path)
    users_file = open(user_file_path, "w")
    for line in self.users_file_original_content:
      users_file.write(line)
    users_file.close()

  def updateUsersFile(self, user_quantity, password, user_file_path):
    self.log("Updating users file: %s" % user_file_path)
    users_file = open(user_file_path, "r")
    file_content = users_file.readlines()
    self.users_file_original_content = file_content
    new_file_content = []
    for line in file_content:
      new_file_content.append(line.replace('<password>', password).replace('<user_quantity>', str(user_quantity)))
    users_file.close()
    os.remove(user_file_path)
    users_file = open(user_file_path, "w")
    for line in new_file_content:
      users_file.write(line)
    users_file.close()

  def run(self):
    self.log("Scalability Launcher started, with:")
    self.log("Test suite master url: %s" %self.__argumentNamespace.test_suite_master_url)
    self.log("Test suite: %s" %self.__argumentNamespace.test_suite)
    self.log("Test result path: %s" %self.__argumentNamespace.test_result_path)
    self.log("Revision: %s" %self.__argumentNamespace.revision)
    self.log("Node title: %s" %self.__argumentNamespace.node_title)
    self.log("ERP5 url: %s" %self.__argumentNamespace.erp5_url)

    error_message_set, exit_status = set(), 0

    # Get suite informations
    suite = makeSuite(self.__argumentNamespace.test_suite, self.__argumentNamespace.erp5_location, self.log)
    test_suite_list = suite.getTestList()

    # Main loop
    # while True:
    try:
      current_test = self.getRunningTest()
    except Exception as e:
      self.log("ERROR while getting current running test")
      self.log(e)
    self.log("Test Case %s going to be run." %(current_test.title))

    # Prepare configuration
    current_test_number = int(current_test.title)
    test_duration = suite.getTestDuration(current_test_number)
    benchmarks_path = os.path.join(self.__argumentNamespace.erp5_location, suite.getTestPath())
    user_file_full_path = os.path.join(self.__argumentNamespace.erp5_location, suite.getUsersFilePath())
    user_file_path = os.path.split(user_file_full_path)[0]
    user_file = os.path.split(user_file_full_path)[1]
    tester_path = self.__argumentNamespace.runner_path
    user_quantity = suite.getUserNumber(current_test_number)
    repetition = suite.getTestRepetition(current_test_number)
    erp5_url = "http://%s/erp5" % self.__argumentNamespace.erp5_url

    self.log("user_quantity: %s" %str(user_quantity))
    self.log("test_duration: %s seconds" %str(test_duration))

    # Store the number of documents generated for each iteration
    document_number = []

    try:
      password = self.createScalabilityUsersInInstance(user_quantity)
    except Exception as e:
      self.log("ERROR")
      self.log(e)
    self.log("Generated password for created users: %s" % password)
    self.updateUsersFile(user_quantity, password, user_file_full_path + ".py")
    self.log("Users file updated.")

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_dir = "test-%s_%s" % (current_test.title, now)
    # Repeat the same test several times to accurate test result
    for i in range(1, repetition+1):
      self.log("Repetition: %d/%d" %(i, repetition))

      # Get the number of documents present before running the test.
      waitFor0PendingActivities(erp5_url, self.log)
      #previous_document_number = getCreatedDocumentNumberFromERP5(self.__argumentNamespace.erp5_url, self.log)
      # Generate commands to run
      command_list = []
      user_index = 0
      for test_suite in test_suite_list:
        command_list.append([tester_path,
             erp5_url,
             str(user_quantity/len(test_suite_list)),
             test_suite,
             '--benchmark-path-list', benchmarks_path,
             '--users-file-path', user_file_path,
             '--users-file', user_file,
             '--filename-prefix', "%s_%s_repetition%d" %(LOG_FILE_PREFIX, current_test.title, i),
             '--report-directory', self.__argumentNamespace.log_path,
             '--repeat', "%s" %str(MAX_DOCUMENTS),
             '--max-errors', str(MAX_ERRORS),
             '--user-index', str(user_index),
        ])
        user_index += user_quantity/len(test_suite_list)

      # Launch commands
      tester_process_list = []
      for command in command_list:
        try:
          self.log("[DEBUG] command: %s" %str(command))
          tester_process_list.append(subprocess.Popen(command))
        except Exception as e:
          self.log("[ERROR] While running command.")
          self.log(traceback.format_exc())
          raise

      # Sleep
      self.log("Going to sleep for %s seconds (Test duration)." % str(test_duration))
      time.sleep(test_duration)

      # Stop
      for tester_process in tester_process_list:
        tester_process.send_signal(signal.SIGINT)
        self.log("End signal sent to the tester.")

      # Count created documents
      # Wait for 0 pending activities before counting
      waitFor0PendingActivities(erp5_url, self.log)
      #current_document_number = getCreatedDocumentNumberFromERP5(self.__argumentNamespace.erp5_url, self.log)
      #created_document_number = current_document_number - previous_document_number
      #document_number.append(created_document_number)
      # Move csv/logs
      self.log("Moving logs to directory '%s'" % log_dir)
      self.moveLogs(log_dir)

    self.log("Test Case %s is finish" %(current_test.title))

    # Get the maximum as choice
    maximum = 0
    for i in range(0,len(document_number)):
      if document_number[i] > maximum:
        maximum = document_number[i]

    # Send results to ERP5 master
    retry_time = 2.0
    proxy = taskdistribution.ServerProxy(
                self.__argumentNamespace.test_suite_master_url,
                allow_none=True
            ).portal_task_distribution
    test_result_line_test = taskdistribution.TestResultLineProxy(
                              proxy, retry_time, self.logger,
                              current_test.relative_path,
                              current_test.title
                            )
    results = "created docs=%d\n"\
              "number of repetitions=%d\n"\
              "duration=%d\n"\
              "number of tests=%d\n"\
              "number of users=%d\n"\
              "tests=%s\n"\
              %(
                maximum,
                repetition,
                test_duration,
                len(test_suite_list),
                (user_quantity/len(test_suite_list))*len(test_suite_list),
                '_'.join(test_suite_list)
              )
    self.log("Results: %s" %results)
    self.log("Stopping the test case...")
    try:
      test_result_line_test.stop(stdout=results,
                      test_count=len(test_suite_list),
                      duration=test_duration)
    except Exception as e:
      self.log("ERROR stopping test line")
      self.log(e)
      raise e
    self.log("Test Case Stopped")
    self.clearUsersFile(user_file_full_path + ".py")
    # end of the main while

    error_message_set = None
    exit_status = 0
    return error_message_set, exit_status

def main():
  error_message_set, exit_status = ScalabilityLauncher().run()
  for error_message in error_message_set:
    print >>sys.stderr, "ERROR: %s" % error_message

  sys.exit(exit_status)
