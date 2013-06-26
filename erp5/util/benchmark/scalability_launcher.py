#!/usr/bin/env python


import argparse
import os
import time
import sys
import multiprocessing
import errno

import logging
import logging.handlers
from .argument import ArgumentType
from .performance_tester import PerformanceTester
from erp5.util import taskdistribution

class ScalabilityTest(object):
  def __init__(self, title, count):
    self.title = title
    self.count = count
    
  def dump(self):
    print '<ScalabilityTest>'
    print 'self.title: %s' %(str(self.title))
    print 'self.count: %s' %(str(self.count))
    
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
    logger = logging.getLogger('scalability_launcher')
    logger.addHandler(logging.NullHandler())
    file_handler = logging.handlers.RotatingFileHandler(
        filename=self.__argumentNamespace.log_path,
        maxBytes=20000000, backupCount=4)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    self.log = logger.info
    
    # Proxy to with erp5 master test_result
    self.test_result = taskdistribution.TestResultProxyProxy(self.__argumentNamespace.portal_url,
              1.0, logger, self.__argumentNamespace.test_result_url,
              self.__argumentNamespace.node_title, self.__argumentNamespace.revision)  

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

  def updateTestResultLineStatus(self, state):
    """
    Update state of a test_result_line
    """
    # TODO : set a line per count value and use setState (?)
    # 
    pass

  def _getNextTest(self):
    """
    Get testsuite parameters
    """
    title = "My Sweet Title"
    count = 1
    next_test = ScalabilityTest(title, count)
    return next_test

  def run(self):
    self.log("Scalability Launcher started")
    max_time = 10
    start_time = time.time()
    error_message_set, exit_status = set(), 0

    test_result = taskdistribution.TestResultProxyProxy(
                        self.__argumentNamespace.test_suite_master_url,
                        1.0, self.log,
                        self.__argumentNamespace.test_result_path,
                        self.__argumentNamespace.node_title,
                        self.__argumentNamespace.revision
                      )
                          
    #self.log("%s", self.test_result.isAlive())
    
    while time.time()-start_time < max_time:
      current_test = self._getNextTest()
      current_test.dump()
      time.sleep(2)
      
      # Here call a runScalabilityTest ( placed on product/ERP5Type/tests ) ?
        
    return error_message_set, exit_status

def main():
  error_message_set, exit_status = ScalabilityLauncher().run()
  for error_message in error_message_set:
    print >>sys.stderr, "ERROR: %s" % error_message

  sys.exit(exit_status)