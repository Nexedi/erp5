#!/usr/bin/env python

from __future__ import division

import argparse
import os
import shutil
import time
import sys
import json
import logging
import logging.handlers
import glob
import threading
from erp5.util.benchmark.thread import TestThread, TestMetricThread
from erp5.util import taskdistribution
from erp5.util.testnode import Utils
from erp5.util.testnode.ProcessManager import ProcessManager
import datetime
from inspect import getargspec

MAX_INSTALLATION_TIME = 60*50
MAX_TESTING_TIME = 60
MAX_GETTING_CONNECTION_TIME = 60*5
TEST_METRIC_TIME_INTERVAL = 60
SCALABILITY_TEST_DURATION = 10*60

SCALABILITY_LOG_FILENAME = "runScalabilityTestSuite"
LOG_FILE_PREFIX = "scalability-test"
MAX_ERRORS = 10

class DummyLogger(object):
  def __init__(self, func):
    for name in ('trace', 'debug', 'info', 'warn', 'warning', 'error',
      'critical', 'fatal'):
       setattr(self, name, func)

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
    self.logger = createLogger(self.__argumentNamespace.log_path)
    self.log = self.logger.info
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

    parser.add_argument('--site-availability-url',
                        metavar='SITE_AVAILABILITY_URL',
                        help='Url to check instance availability')

    parser.add_argument('--serialise-test',
                        metavar='SERIAL_TEST',
                        action='store_true',
                        help='Without this option, all test methods are invoked in parallel')

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
    self.log("Logs were moved from %s to %s" % (
      self.__argumentNamespace.log_path, new_directory_path))

  def getRunningTest(self):
    """
    Return a ScalabilityTest with current running test case informations
    """
    data_array = self.__argumentNamespace.current_test_data.split(',')
    data = json.dumps({"count": data_array[0], "title": data_array[1], "relative_path": data_array[2]})
    encoded_data = Utils.deunicodeData(json.loads(data))
    return ScalabilityTest(encoded_data, self.test_result)

  def clearUsersFile(self, user_file_path):
    self.log("Clearing users file: %s" % user_file_path)
    os.remove(user_file_path)
    with open(user_file_path, "w") as users_file:
      for line in self.users_file_original_content:
        users_file.write(line)

  def updateUsersFile(self, user_quantity, password, user_file_path):
    self.log("Updating users file: %s" % user_file_path)
    with open(user_file_path, "r") as users_file:
      file_content = users_file.readlines()
    self.users_file_original_content = file_content
    new_file_content = []
    for line in file_content:
      new_file_content.append(line.replace('<password>', password).replace('<user_quantity>', str(user_quantity)))
    os.remove(user_file_path)
    with open(user_file_path, "w") as users_file:
      for line in new_file_content:
        users_file.write(line)

  def run(self):
    self.log("Scalability Launcher started, with:")
    self.log("Test suite master url: %s" %self.__argumentNamespace.test_suite_master_url)
    self.log("Test suite: %s" %self.__argumentNamespace.test_suite)
    self.log("Test result path: %s" %self.__argumentNamespace.test_result_path)
    self.log("Revision: %s" %self.__argumentNamespace.revision)
    self.log("Node title: %s" %self.__argumentNamespace.node_title)
    self.log("Instance url: %s" %self.__argumentNamespace.instance_url)

    error_message_set, exit_status = set(), 0
    process_manager = ProcessManager()

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
    benchmarks_path = os.path.join(self.__argumentNamespace.repo_location, suite.getTestPath())
    user_file_full_path = os.path.join(self.__argumentNamespace.repo_location, suite.getUsersFilePath())
    user_file_path = os.path.split(user_file_full_path)[0]
    user_file = os.path.split(user_file_full_path)[1]
    tester_path = self.__argumentNamespace.runner_path
    instance_url = self.__argumentNamespace.instance_url
    metric_url = self.__argumentNamespace.metric_url
    site_availability_url = self.__argumentNamespace.site_availability_url
    serialise_test = self.__argumentNamespace.serialise_test

    # To take metrics
    metric_thread_stop_event = threading.Event()
    metric_thread = TestMetricThread(metric_url, site_availability_url, self.log, metric_thread_stop_event, interval=TEST_METRIC_TIME_INTERVAL)
    metric_thread.start()

    bootstrap_password = self.__argumentNamespace.bootstrap_password
    # Prepare users
    user_quantity_dict = {}
    total_user_quantity = 0
    for test_suite in test_suite_list:
      if 'test_name' in getargspec(suite.getUserQuantity).args:
        user_quantity = suite.getUserQuantity(current_test_number, test_suite)
      else:
        user_quantity = suite.getUserQuantity(current_test_number)
      user_quantity_dict[test_suite] = user_quantity
      total_user_quantity += user_quantity
    try:
      self.updateUsersFile(total_user_quantity, bootstrap_password, user_file_full_path + ".py")
    except Exception as e:
      self.log("ERROR while updating file: " + str(e))

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_dir = "test-%s_%s" % (current_test.title, now)

    user_index = 0
    max_test_duration = 0.0
    exec_env = os.environ.copy()
    exec_env.update({'raise_error_if_fail': False})
    # Prepare commands
    for index, test_suite in enumerate(test_suite_list, start=1):
      getTestDuration = getattr(suite, 'getTestDuration', None)
      if getTestDuration is not None:
        if len(getargspec(getTestDuration).args) == 3:
          test_duration = getTestDuration(current_test_number, test_suite)
        else:
          test_duration = getTestDuration(current_test_number)
      else:
        test_duration = 0
      getTestRepeat = getattr(suite, 'getTestRepeat', None)
      if getTestRepeat is not None:
        if len(getargspec(getTestRepeat).args) == 3:
          test_repeat = getTestRepeat(current_test_number, test_suite)
        else:
          test_repeat = getTestRepeat(current_test_number)
      else:
        test_repeat = -1
      if not test_duration:
        test_duration = SCALABILITY_TEST_DURATION
      if max_test_duration < test_duration:
        max_test_duration = test_duration
      log_file_name_prefix = "%s_%s_suite_%s" %(LOG_FILE_PREFIX, current_test.title, test_suite)
      command = [tester_path,
                           instance_url,
                           str(user_quantity_dict[test_suite]),
                           test_suite,
                           '--benchmark-path-list', benchmarks_path,
                           '--users-file-path', user_file_path,
                           '--users-file', user_file,
                           '--filename-prefix', log_file_name_prefix,
                           '--report-directory', self.__argumentNamespace.log_path,
                           '--max-errors', str(MAX_ERRORS),
                           '--user-index', str(user_index),
                           "--repeat", "%d"%test_repeat,
                           "--duration", "%d"%test_duration,
                         ]
      user_index += user_quantity_dict[test_suite]
      # Launch command
      test_thread = TestThread(process_manager, command, self.log, env=exec_env)
      test_thread.start()
      if serialise_test:
        self.log("Going to sleep for %s seconds." % str(test_duration))
        test_thread.join(test_duration)
        if test_thread.is_alive():
          process_manager.killPreviousRun()
    if not serialise_test:
      # Sleep
      self.log("Going to sleep for %s seconds." % str(max_test_duration))
      time.sleep(max_test_duration)
      process_manager.killPreviousRun()
    self.moveLogs(log_dir, current_test)

    self.log("Test Case %s has finished" %(current_test.title))
    metric_thread_stop_event.set()
    time.sleep(15) # wait thread to stop
    metric_list = metric_thread.getMetricList()
    test_output = suite.getScalabilityTestOutput(metric_list)
    if not test_output:
      metric_error = metric_thread.getErrorMessage()
      if metric_error:
        error_message = str(metric_error)
      else:
        error_message = "Metric thread couldn't get any metric"
      error_message_set.add(error_message)

    if error_message_set:
      self.log("error_message_set: " + str(error_message_set))

    test_details = "number of users=%d\n"\
                    "number of tests=%d\n"\
                    "tests=%s\n"\
                    "maximum duration=%d\n"\
                    %(
                      total_user_quantity,
                      len(test_suite_list),
                      '_'.join(test_suite_list),
                      max_test_duration
                    )
    self.log("Test details: %s" % test_details)

    # Send results to master
    self.log("Connecting to master to set test results...")
    try:
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
      if len(error_message_set):
        self.log("Test case failed.")
        error_message = "; ".join(str(error) for error in error_message_set)
        test_result_line_test.stop(error_count=1, failure_count=1,
                                   command=test_details,
                                   stdout=error_message, stderr=error_message)
      else:
        self.log("Test case finished. Output: %s" % test_output)
        test_result_line_test.stop(stdout=test_output,
                                   command=test_details,
                                   test_count=len(test_suite_list),
                                   duration=max_test_duration)
    except Exception as e:
      self.log("Error during communication to master: " + str(e))
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
