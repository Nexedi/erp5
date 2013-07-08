#!/usr/bin/env python


import argparse
import os
import time
import sys
import multiprocessing
import errno
import json
import logging
import logging.handlers
from erp5.util.benchmark.argument import ArgumentType
from erp5.util.benchmark.performance_tester import PerformanceTester
from erp5.util import taskdistribution
from erp5.util.testnode import testnodeUtils

from subprocess import call

class ScalabilityTest(object):
  def __init__(self, data, test_result):
    self.__dict__ = {}
    self.__dict__.update(data)
    self.test_result = test_result

  def stop(self):
    self.test_result.stopTestCase(self.relative_path)
    
  def cancel(self):
    self.test_result.cancelTestCase(self.relative_path)
    
    
class ScalabilityLauncher(object):
  def __init__(self):
    # Parse arguments
    self.__argumentNamespace = self._parseArguments(argparse.ArgumentParser(
          description='Run ERP5 benchmarking scalability suites.'))
    # Create Logger
    logger_format = '%(asctime)s %(name)-13s: %(levelname)-8s %(message)s'
    formatter = logging.Formatter(logger_format)
    logging.basicConfig(level=logging.INFO,
                     format=logger_format)
    logger = logging.getLogger('runScalabilityTestSuite')
    logger.addHandler(logging.NullHandler())
    file_handler = logging.handlers.RotatingFileHandler(
        filename=self.__argumentNamespace.log_path,
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

  def getNextTest(self):
    """
    Return a ScalabilityTest with current running test case informations,
    or None if no test_case ready
    """
    data = self.test_result.getNextTestCase()
    if data == None :
      return None
    decoded_data = testnodeUtils.deunicodeData(json.loads(
                  data
                ))
    next_test = ScalabilityTest(decoded_data, self.test_result)
    return next_test

  def run(self):
    self.log("Scalability Launcher started")
    max_time = 36000
    start_time = time.time()
    error_message_set, exit_status = set(), 0

    test_suites = 'createPerson createWebPage'
    benchmark_path_list = ''
    user_file_path = ''
    
    while time.time()-start_time < max_time:
      current_test = self.getNextTest()
      if current_test == None:
        self.log("No Test Case Ready")
        time.sleep(5)
      else:
        # Here call a runScalabilityTest ( placed on product/ERP5Type/tests ) ?
        self.log("Test Case %s is running..." %(current_test.title))
        # Call the performance_tester_erp5
        call(["performance_tester_erp5",
               self.__argumentNamespace.erp5_url,
               '1',
               test_suites,
               '--benchmark-path-list', benchmark_path_list,
               '--users-file-path', user_file_path
            ]) 
        self.log("Test Case %s is finish" %(current_test.title))
        current_test.stop()
        self.log("Test Case Stopped")
      
    return error_message_set, exit_status

def main():
  error_message_set, exit_status = ScalabilityLauncher().run()
  for error_message in error_message_set:
    print >>sys.stderr, "ERROR: %s" % error_message

  sys.exit(exit_status)
