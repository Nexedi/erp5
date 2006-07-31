#!/usr/bin/python
import os
import sys
import getopt

__doc__ = """%(program)s: unit test runner for the ERP5 Project

usage: %(program)s [options] [UnitTest1[:TestClass1[:TestClass2]] [UnitTest2]]

Options:
  -v, --verbose              produce verbose output
  -h, --help                 this help screen
  --erp5_sql_connection_string=STRING
                             ZSQL Connection string for erp5_sql_connection, by
                             default, it will use "test test"                            
  --cmf_activity_sql_connection_string=STRING
                             ZSQL Connection string for
                             cmf_activity_sql_connection (if unset, defaults to
                             erp5_sql_connection_string)
  --erp5_sql_deferred_connection_string=STRING 
                             ZSQL Connection string for
                             erp5_sql_deferred_connection (if unset, defaults
                             to erp5_sql_connection_string)
 
"""


def initializeInstanceHome(tests_framework_home,
                           real_instance_home,
                           instance_home):
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
  software_home = '/usr/lib/zope/lib/python'

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
  os.environ.setdefault('EVENT_LOG_FILE', os.path.join(tests_home, 'zLOG.log'))
  os.environ.setdefault('EVENT_LOG_SEVERITY', '-300')

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
  sys.path.extend(product_test_list)
  sys.path.extend((real_tests_home, tests_home))

  # Make sure that locally overridden python modules are used
  sys.path.insert(0, os.path.join(real_instance_home, 'lib', 'python'))

  # XXX Allowing to load modules from here is a wrong idea. use the above path
  # instead.
  # Add tests_framework_home as first path element.
  # this allows to bypass psyco by creating a dummy psyco module
  # it is then possible to run the debugger by "import pdb; pdb.set_trace()"
  sys.path.insert(0, tests_framework_home)
 
  filtered_tests_class_names = 0
  for test in test_list:
    if ':' in test:
      test_module = test.split(':')[0]
      if test_module.endswith('.py'):
        test_module = test_module[:-3]
      test_class_list = test.split(':')[1:]
      filtered_tests_class_names = 1
    else:
      if test.endswith('.py'):
        test = test[:-3]
      test_module = test
      test_class_list = None
    m = __import__(test_module)
    if not filtered_tests_class_names and hasattr(m, 'test_suite'):
      suite.addTest(m.test_suite())
    else:
      # dynamically create the test suite using class names passed on the
      # command line.
      for attr_name in dir(m):
        attr = getattr(m, attr_name)
        if (type(attr) == type(type)) and (hasattr(attr, '__module__')) and \
            (attr.__module__ == test_module) :
          if test_class_list is None or attr.__name__ in test_class_list:
            suite.addTest(unittest.makeSuite(attr))

  return TestRunner().run(suite)

def usage(stream, msg=None):
  if msg:
    print >>stream, msg
    print >>stream
  program = os.path.basename(sys.argv[0])
  print >>stream, __doc__ % {"program": program}

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:],
        "hv", ["help", "verbose", "erp5_sql_connection_string=",
        "cmf_activity_sql_connection_string=", "erp5_deferred_sql_connection_string="] )
  except getopt.GetoptError, msg:
    usage(sys.stderr, msg)
    sys.exit(2)
  
  for opt, arg in opts:
    if opt in ("-v", "--verbose"):
      os.environ['VERBOSE'] = "1"
    elif opt in ("-h", "--help"):
      usage(sys.stdout)
      sys.exit()
    elif opt == "--erp5_sql_connection_string":
      os.environ["erp5_sql_connection_string"] = arg
      print "set to ", arg
    elif opt == "--cmf_activity_sql_connection_string":
      os.environ["cmf_activity_sql_connection_string"] = arg
    elif opt == "--erp5_sql_deferred_connection_string":
      os.environ["erp5_sql_deferred_connection_string"] = arg

  test_list = args
  if not test_list:
    print "No test to run, exiting immediately."
    sys.exit(1)
  
  result = runUnitTestList(test_list=test_list)
  sys.exit(len(result.failures) + len(result.errors))

if __name__ == '__main__':
  main()
