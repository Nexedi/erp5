#!/usr/bin/python
#
# Runs the tests passed on the command line
#
import os, sys

def getUnitTestFile() :
  return os.path.abspath(__file__)

# site specific variables
instance_home = '/home/%s/zope' % os.environ['USER']
software_home = '/usr/lib/zope/lib/python'
tests_home = os.path.join(instance_home, 'tests')
tests_framework_home = os.path.dirname(os.path.abspath(__file__))

if '__INSTANCE_HOME' not in globals().keys() :
  __INSTANCE_HOME = instance_home

def runUnitTestList(test_list) :
  if len(test_list) == 0 :
    print "No test to run, exiting immediately."
    return
  os.environ['INSTANCE_HOME'] = instance_home
  os.environ['SOFTWARE_HOME'] = software_home
  os.environ['COPY_OF_INSTANCE_HOME'] = instance_home
  os.environ['COPY_OF_SOFTWARE_HOME'] = software_home

  execfile(os.path.join(tests_framework_home, 'framework.py')) 

  import unittest
  from Testing import ZopeTestCase

  TestRunner = unittest.TextTestRunner
  suite = unittest.TestSuite()

  os.chdir(tests_home)

  # allow unit tests of our Products to be reached.
  products_home = os.path.join(instance_home, 'Products')
  from glob import glob
  product_test_list = glob(products_home + os.sep + '*' + os.sep + 'tests')
  sys.path += product_test_list

  for test in test_list:
    m = __import__(test)
    for attr_name in dir(m) :
      attr = getattr(m, attr_name)
      if (type(attr) == type(type)) and (hasattr(attr, '__module__')) and (attr.__module__ == test) :
        suite.addTest(unittest.makeSuite(attr))

  TestRunner().run(suite)

if __name__ == '__main__' :
  test_list = sys.argv[1:]
  if len(test_list) == 0 :
    print "No test to run, exiting immediately."
    print "Usage : %s UnitTest1 UnitTest2 ..." % sys.argv[0]
    sys.exit(1)
  runUnitTestList(test_list=test_list)
