#!/usr/bin/env python

import argparse
import os
import shutil
import time
import sys
import multiprocessing
import signal
import errno
import json
import logging
import logging.handlers
import glob
import urlparse
import httplib
import base64
import threading
from erp5.util.benchmark.argument import ArgumentType
from erp5.util.benchmark.performance_tester import PerformanceTester
from erp5.util.benchmark.thread import TestThread, TestMetricThread
from erp5.util import taskdistribution
from erp5.util.testnode import Utils
from erp5.util.testnode.ProcessManager import SubprocessError, ProcessManager, CancellationError
import datetime

MAX_INSTALLATION_TIME = 60*50
MAX_TESTING_TIME = 60
MAX_GETTING_CONNECTION_TIME = 60*5
TEST_METRIC_TIME_INTERVAL = 60*3

SCALABILITY_LOG_FILENAME = "runScalabilityTestSuite"
LOG_FILE_PREFIX = "scalability-test"
MAX_ERRORS = 2

class DummyLogger(object):
  def __init__(self, func):
    for name in ('trace', 'debug', 'info', 'warn', 'warning', 'error',
      'critical', 'fatal'):
       setattr(self, name, func)

def getConnection(instance_url, log):
  """
  Return a connection with the instance.
  """
  start_time = time.time()
  count = 0
  while MAX_GETTING_CONNECTION_TIME > time.time()-start_time:
    try:
      count = count + 1
      parsed = urlparse.urlparse(instance_url)
      host = "%s:%s" % (parsed.hostname, str(parsed.port))
      if parsed.port is None: host = parsed.hostname
      if parsed.scheme == 'https':
        return httplib.HTTPSConnection(host)
      elif parsed.scheme == 'http':
        return httplib.HTTPConnection(host)
      else:
        raise ValueError("Protocol not implemented")
    except:
      log("Can't get connection to %s, we will retry." %instance_url)
      time.sleep(10)
  raise ValueError("Cannot get new connection after %d try (for %s s)" %(count, str(time.time()-start_time)))

# TODO: this will be refactored soon
def waitFor0PendingActivities(instance_url, log):
  """
  Waiting while there are no pending activities on the instance.
  """
  log("waiting activities for: " + str(instance_url))
  start_time = time.time()
  parsed = urlparse.urlparse(instance_url)
  user = parsed.username;
  password = parsed.password;
  header_dict = {'Authorization': 'Basic %s' % \
  base64.encodestring('%s:%s' % (user, password)).strip()}

  count = 0
  ok = False
  while MAX_INSTALLATION_TIME > time.time()-start_time and not ok:
    zope_connection = getConnection(instance_url, log)
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
    except Exception as e:
      time.sleep(5)
      log("exception: " + str(e))
      log("Getting activities failed, retry.")

  if not ok:
    raise ValueError("Cannot waitFor0PendingActivities after %d try (for %s s)" %(count, str(time.time()-start_time)))

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
  except Exception as e:
    log("[ERROR] While making suite: " + str(e))
    raise
  return suite

def createLogger(log_path):
  log_path = os.path.join(log_path, SCALABILITY_LOG_FILENAME + ".log")
  logger_format = '%(asctime)s %(name)-13s: %(levelname)-8s %(message)s'
  formatter = logging.Formatter(logger_format)
  logging.basicConfig(level=logging.INFO,
                     format=logger_format)
  logger = logging.getLogger(SCALABILITY_LOG_FILENAME)
  file_handler = logging.handlers.RotatingFileHandler(
                  filename=log_path,
                  maxBytes=20000000, backupCount=4)
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)
  return logger

class ScalabilityLauncher(object):
  def __init__(self):
    self.__argumentNamespace = self._parseArguments(argparse.ArgumentParser(
          description='Run benchmarking scalability suites.'))
    logger = createLogger(self.__argumentNamespace.log_path)
    self.log = logger.info
    self.logger = logger
    self.users_file_original_content = []
    # Proxy to with master test_result
    portal_url = self.__argumentNamespace.test_suite_master_url
    distributor = taskdistribution.TaskDistributor(portal_url, logger=DummyLogger(self.log))
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
    parser.add_argument('--instance-url',
                        metavar='INSTANCE_URL',
                        help='Main url of instance to test')

    parser.add_argument('--bootstrap-password',
                        metavar='BOOTSRAP_PASSWORD',
                        help='Bootstrap password of instance objects')

    parser.add_argument('--test-result-path',
                        metavar='TEST_RESULT_PATH',
                        help='Relative path of the test result')

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
                        help='Url to connect to the Master testsuite taskditributor')

    parser.add_argument('--log-path',
                        metavar='LOG_PATH',
                        help='Log Path')

    parser.add_argument('--repo-location',
                        metavar='REPO_LOCATION',
                        help='Path to repository')

    parser.add_argument('--runner-path',
                        metavar='RUNNER_PATH',
                        help='runner Path')

    parser.add_argument('--metric-url',
                        metavar='METRIC_URL',
                        help='Url to connect to instance metric generator')

  @staticmethod
  def _checkParsedArguments(namespace):
    return namespace

  @staticmethod
  def _parseArguments(parser):
    ScalabilityLauncher._addParserArguments(parser)
    namespace = parser.parse_args()
    ScalabilityLauncher._checkParsedArguments(namespace)
    return namespace

  def moveLogs(self, folder_name, current_test):
    file_to_move_list = glob.glob(os.path.join(self.__argumentNamespace.log_path,
                                  "%s*.csv" %LOG_FILE_PREFIX))
    file_to_move_list += glob.glob(os.path.join(self.__argumentNamespace.log_path,
                                  "%s*.log" %LOG_FILE_PREFIX))
    root_test_dir = os.path.join(self.__argumentNamespace.log_path,
                                 "scalability-test-%s/" % current_test.relative_path.split("/")[1])
    if not os.path.exists(root_test_dir):
      os.makedirs(root_test_dir)
    new_directory_path = os.path.join(root_test_dir,
                                      folder_name)
    if not os.path.exists(new_directory_path):
      os.makedirs(new_directory_path)
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
    self.log("Instance url: %s" %self.__argumentNamespace.instance_url)

    error_message_set, exit_status = set(), 0
    process_manager = ProcessManager(self.log)

    # Get suite informations
    suite = makeSuite(self.__argumentNamespace.test_suite, self.__argumentNamespace.repo_location, self.log)
    test_suite_list = suite.getTestList()

    try:
      current_test = self.getRunningTest()
    except Exception as e:
      error_message = "ERROR while getting current running test: " + str(e)
      self.log(error_message)
      return error_message, 1

    self.log("Test Case %s going to be run." %(current_test.title))
    # Prepare configuration
    current_test_number = int(current_test.title)
    test_duration = suite.getTestDuration(current_test_number)
    benchmarks_path = os.path.join(self.__argumentNamespace.repo_location, suite.getTestPath())
    user_file_full_path = os.path.join(self.__argumentNamespace.repo_location, suite.getUsersFilePath())
    user_file_path = os.path.split(user_file_full_path)[0]
    user_file = os.path.split(user_file_full_path)[1]
    tester_path = self.__argumentNamespace.runner_path
    user_quantity = suite.getUserQuantity(current_test_number)
    repetition = suite.getTestRepetition(current_test_number)
    instance_url = self.__argumentNamespace.instance_url
    metric_url = self.__argumentNamespace.metric_url

    # To take metrics
    metric_thread_stop_event = threading.Event()
    metric_thread = TestMetricThread(metric_url, self.log, metric_thread_stop_event, interval=TEST_METRIC_TIME_INTERVAL)
    metric_thread.start()

    bootstrap_password = self.__argumentNamespace.bootstrap_password
    try:
      self.updateUsersFile(user_quantity, bootstrap_password, user_file_full_path + ".py")
    except Exception as e:
      self.log("ERROR while updating file: " + str(e))

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_dir = "test-%s_%s" % (current_test.title, now)
    # the repetition of tests will be refactored soon
    for i in range(1, repetition+1):
      self.log("Repetition: %d/%d" %(i, repetition))
      waitFor0PendingActivities(instance_url, self.log)
      # Generate commands to run
      command_list = []
      user_index = 0
      for test_suite in test_suite_list:
        command_list.append([tester_path,
                             instance_url,
                             str(user_quantity/len(test_suite_list)),
                             test_suite,
                             '--benchmark-path-list', benchmarks_path,
                             '--users-file-path', user_file_path,
                             '--users-file', user_file,
                             '--filename-prefix', "%s_%s_repetition%d_suite_%s" %(LOG_FILE_PREFIX, current_test.title, i, test_suite),
                             '--report-directory', self.__argumentNamespace.log_path,
                             '--repeat', "%d"%1,
                             '--max-errors', str(MAX_ERRORS),
                             '--user-index', str(user_index),
                           ])
        user_index += user_quantity/len(test_suite_list)

      # Launch commands
      for command in command_list:
        test_thread = TestThread(process_manager, command, self.log)
        test_thread.start()
      # Sleep
      self.log("Going to sleep for %s seconds (Test duration)." % str(test_duration))
      time.sleep(test_duration)

      waitFor0PendingActivities(instance_url, self.log)
      self.moveLogs(log_dir, current_test)

    self.log("Test Case %s has finished" %(current_test.title))
    metric_thread_stop_event.set()
    time.sleep(15) # wait thread to stop
    metric_list = metric_thread.getMetricList()
    test_output = suite.getScalabilityTestOutput(metric_list)
    if not test_output:
      self.log("metric list and test output empty. getting metric thread error message.")
      test_output = metric_thread.getErrorMessage()
    self.log("test_output: " + str(test_output))

    # Send results to master
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
    test_details = "number of users=%d\n"\
                    "number of repetitions=%d\n"\
                    "number of tests=%d\n"\
                    "tests=%s\n"\
                    "duration=%d\n"\
                    %(
                      (user_quantity/len(test_suite_list))*len(test_suite_list),
                      repetition,
                      len(test_suite_list),
                      '_'.join(test_suite_list),
                      test_duration
                    )
    self.log("Test details: %s" % test_details)
    self.log("Test output: %s" % test_output)
    self.log("Stopping the test case...")
    try:
      test_result_line_test.stop(stdout=test_output,
                      command=test_details,
                      test_count=len(test_suite_list),
                      duration=test_duration)
    except Exception as e:
      self.log("ERROR stopping test line")
      self.log(e)
      raise e
    self.log("Test Case Stopped")
    self.clearUsersFile(user_file_full_path + ".py")

    error_message_set = None
    exit_status = 0
    self.log("Scalability Launcher finished.")
    return error_message_set, exit_status

def main():
  error_message_set, exit_status = ScalabilityLauncher().run()
  sys.exit(exit_status)
