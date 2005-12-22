#!/usr/bin/python
#
# Runs the tests passed on the command line
#
import os, sys

def getUnitTestFile() :
  return os.path.abspath(__file__)

def initializeInstanceHome(tests_framework_home, real_instance_home, instance_home):
  if not os.path.exists(instance_home):
    os.mkdir(instance_home)
  for d in ('Constraint', 'Document', 'PropertySheet', 'tests', 'var'):
    path = os.path.join(instance_home, d)
    if not os.path.exists(path):
      os.mkdir(path)
  for d in ('Extensions', 'Products', 'bt5'):
    src = os.path.join(real_instance_home, d)
    dst = os.path.join(instance_home, d)
    if not os.path.exists(dst):
      os.symlink(src, dst)
  src = os.path.join(tests_framework_home, 'custom_zodb.py')
  dst = os.path.join(instance_home, 'custom_zodb.py')
  if not os.path.exists(dst):
    os.symlink(src, dst)

# site specific variables
# handle 64bit architecture
if os.path.isdir('/usr/lib64/zope/lib/python'):
  software_home = '/usr/lib64/zope/lib/python'
else:
  software_home = '/home/yo/tmp/zope-2.8/lib/python'

tests_framework_home = os.path.dirname(os.path.abspath(__file__))
# handle 'system global' instance
if tests_framework_home.startswith('/usr/lib'):
  real_instance_home = '/var/lib/zope'
else:
  real_instance_home = os.path.sep.join(
      tests_framework_home.split(os.path.sep)[:-3])

instance_home = os.path.join(real_instance_home, 'unit_test')
real_tests_home = os.path.join(real_instance_home, 'tests')
tests_home = os.path.join(instance_home, 'tests')

initializeInstanceHome(tests_framework_home, real_instance_home, instance_home)

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
  os.environ['EVENT_LOG_FILE'] = os.path.join(tests_home, 'zLOG.log')
  os.environ['EVENT_LOG_SEVERITY'] = '-300'

  execfile(os.path.join(tests_framework_home, 'framework.py')) 

  import unittest
  from Testing import ZopeTestCase

  try:
    # On Zope 2.8, ZopeTestCase does not have any logging facility.
    # So we must emulate the usual Zope startup code to catch log
    # messages.
    from ZConfig.matcher import SectionValue
    from ZConfig.components.logger.handlers import FileHandlerFactory
    from ZConfig.components.logger.logger import EventLogFactory
    import logging
    section = SectionValue({'dateformat': '%Y-%m-%dT%H:%M:%S', 
                            'format': '------\n%(asctime)s %(levelname)s %(name)s %(message)s', 
                            'level': logging.INFO, 
                            'path': os.environ['EVENT_LOG_FILE']}, 
                           None, None)
    section.handlers = [FileHandlerFactory(section)]
    eventlog = EventLogFactory(section)
    logger = logging.getLogger()
    logger.handlers = []
    eventlog()
  except ImportError:
    pass
  
  TestRunner = unittest.TextTestRunner
  suite = unittest.TestSuite()

  os.chdir(tests_home)

  # allow unit tests of our Products to be reached.
  products_home = os.path.join(instance_home, 'Products')
  from glob import glob
  product_test_list = glob(products_home + os.sep + '*' + os.sep + 'tests')
  sys.path += product_test_list
  sys.path.extend((real_tests_home, tests_home))

  # Add tests_framework_home as first path element.
  # this allows to bypass psyco by creating a dummy psyco module
  # it is then possible to run the debugger by "import pdb; pdb.set_trace()"
  sys.path.insert(0, tests_framework_home)

  for test in test_list:
    if test.endswith('.py'):
      test = test[:-3]
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
