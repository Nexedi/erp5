#!/usr/bin/python2.6
import argparse, pprint, socket, sys, time, xmlrpclib
import DummyTaskDistributionTool
from ERP5TypeTestSuite import ERP5TypeTestSuite

def makeSuite(node_quantity=None, test_suite=None, revision=None,
              db_list=None):
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
  suite = suite_class(revision=revision,
                      max_instance_count=node_quantity,
                      mysql_db_list=db_list.split(','),
                      )
  return suite

def safeRpcCall(function, *args):
  retry = 64
  while True:
    try:
      return function(*args)
    except (socket.error, xmlrpclib.ProtocolError), e:
      print >>sys.stderr, e
      pprint.pprint(args, file(function._Method__name, 'w'))
      time.sleep(retry)
      retry += retry >> 1

def main():
  parser = argparse.ArgumentParser(description='Run a test suite.')
  parser.add_argument('--test_suite', help='The test suite name')
  parser.add_argument('--test_suite_title', help='The test suite title',
                      default=None)
  parser.add_argument('--test_node_title', help='The test node title',
                      default=None)
  parser.add_argument('--project_title', help='The project title',
                      default=None)
  parser.add_argument('--revision', help='The revision to test',
                      default='dummy_revision')
  parser.add_argument('--node_quantity', help='Number of parallel tests to run',
                      default=1, type=int)
  parser.add_argument('--master_url',
                      help='The Url of Master controling many suites',
                      default=None)
  parser.add_argument('--master_directory',
                      help='Directory to simulate master',
                      default=None)
  parser.add_argument('--db_list', help='A list of sql connection strings')
  # parameters that needs to be passed to runUnitTest
  parser.add_argument('--conversion_server_hostname', default=None)
  parser.add_argument('--conversion_server_port', default=None)
  parser.add_argument('--volatile_memcached_server_hostname', default=None)
  parser.add_argument('--volatile_memcached_server_port', default=None)
  parser.add_argument('--persistent_memcached_server_hostname', default=None)
  parser.add_argument('--persistent_memcached_server_port', default=None)
  
  args = parser.parse_args()
  if args.master_url is not None:
    master_url = args.master_url
    if master_url[-1] != '/':
      master_url += '/'
    master = xmlrpclib.ServerProxy("%s%s" %
              (master_url, 'portal_task_distribution'),
              allow_none=1)
    assert master.getProtocolRevision() == 1
  elif args.master_directory is not None:
    master = DummyTaskDistributionTool.JSONFSTaskDistributionTool(
        args.master_directory)
  else:
    master = DummyTaskDistributionTool.DummyTaskDistributionTool()
  test_suite_title = args.test_suite_title or args.test_suite
  revision = args.revision
  suite = makeSuite(test_suite=args.test_suite,
                    node_quantity=args.node_quantity,
                    revision=revision,
                    db_list=args.db_list)
  test_result = safeRpcCall(master.createTestResult,
    args.test_suite, revision, suite.getTestList(),
    suite.allow_restart, test_suite_title, args.test_node_title,
    args.project_title)
  if test_result:
    test_result_path, test_revision = test_result
    while suite.acquire():
      test = safeRpcCall(master.startUnitTest, test_result_path,
                          suite.running.keys())
      if test:
        suite.start(test[1], lambda status_dict, __test_path=test[0]:
          safeRpcCall(master.stopUnitTest, __test_path, status_dict))
      elif not suite.running:
        break
