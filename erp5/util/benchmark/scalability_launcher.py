#!/usr/bin/env python


import argparse
import os
import time
import sys
import multiprocessing
import errno

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
  def __init__(self, namespace=None):
    if not namespace:
      self.__argumentNamespace = self._parseArguments(argparse.ArgumentParser(
          description='Run ERP5 benchmarking scalability suites.'))
    else:
      self.__argumentNamespace = namespace

    # Here make a connection with erp5 master
    portal_url = __argumentNamespace.test_result_url
    result = taskdistribution.TestResultProxyProxy(portal_url, 1.0,
                self._logger, __argumentNamespace.test_result_url,
                __argumentNamespace.node_title, __argumentNamespace.revision)      

  @staticmethod
  def _addParserArguments(parser):
    # Mandatory arguments
    parser.add_argument('--erp5-url',
                        metavar='ERP5_URL',
                        help='Main url of ERP5 instance to test')

    parser.add_argument('--erp5-test-result-url',
                        metavar='ERP5_TEST_RESULT_URL',
                        help='ERP5 URL to find test results corresponding '
                             'to the current running test_suite')
                             
    parser.add_argument('--revision',
                        metavar='REVISION',
                        help='Revision of the test_suite')
                              
    parser.add_argument('--node-title',
                        metavar='NODE_TITLE',
                        help='Title of the testnode which is running this'
                              'launcher')
   
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
    max_time = 10 
    start_time = time.time()
    error_message_set, exit_status = set(), 0
    
    print self.__argumentNamespace.erp5_test_result_url
    print self.__argumentNamespace.erp5_url
    print self.__argumentNamespace.revision
    print self.__argumentNamespace.node_title
      
    while time.time()-start_time < max_time:
      current_test = self._getNextTest()
      current_test.dump()
      time.sleep(2)

    return error_message_set, exit_status

def main():
  error_message_set, exit_status = ScalabilityLauncher().run()
  for error_message in error_message_set:
    print >>sys.stderr, "ERROR: %s" % error_message

  sys.exit(exit_status)