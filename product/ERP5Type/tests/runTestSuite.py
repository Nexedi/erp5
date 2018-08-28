#!/usr/bin/env python2.7
import argparse, sys
from erp5.util import taskdistribution

# XXX: This import is required, just to populate sys.modules['test_suite'].
# Even if it's not used in this file. Yuck.
import ERP5TypeTestSuite

def _parsingErrorHandler(data, _):
  print >> sys.stderr, 'Error parsing data:', repr(data)
taskdistribution.patchRPCParser(_parsingErrorHandler)

def makeSuite(
    node_quantity=None,
    test_suite=None,
    revision=None,
    db_list=None,
    zserver_address_list=None,
    zserver_frontend_url_list=None,
    **kwargs):
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
                      zserver_address_list=zserver_address_list.split(','),
                      zserver_frontend_url_list=zserver_frontend_url_list.split(','),
                      **kwargs)
  return suite

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
  parser.add_argument('--db_list', help='A list of comma separated sql connection strings')
  parser.add_argument('--zserver_address_list', help='A list of comma seperated host:port for Zserver')
  parser.add_argument(
      '--zserver_frontend_url_list',
      help='A list of comma seperated frontend URLs, one for each of zserver_address_list, in the same order')
  # parameters that needs to be passed to runUnitTest
  parser.add_argument('--conversion_server_url', default=None)
  parser.add_argument('--conversion_server_retry_count', default=None)
  parser.add_argument('--conversion_server_hostname', default=None)
  parser.add_argument('--conversion_server_port', default=None)
  parser.add_argument('--volatile_memcached_server_hostname', default=None)
  parser.add_argument('--volatile_memcached_server_port', default=None)
  parser.add_argument('--persistent_memcached_server_hostname', default=None)
  parser.add_argument('--persistent_memcached_server_port', default=None)
  parser.add_argument('--bt5_path', default=None)
  parser.add_argument("--xvfb_bin", default=None)
  parser.add_argument("--firefox_bin", default=None)

  args = parser.parse_args()
  if args.bt5_path is not None:
    sys.path[0:0] = args.bt5_path.split(",")
  master = taskdistribution.TaskDistributor(args.master_url)
  test_suite_title = args.test_suite_title or args.test_suite
  revision = args.revision

  if len(args.zserver_address_list.split(",")) < args.node_quantity:
    print >> sys.stderr, 'Not enough zserver address/frontends for node quantity %s (%r)' % (
        args.node_quantity, args.zserver_address_list)
    sys.exit(1)

  # sanity check
  assert len(args.zserver_address_list.split(",")) == len(args.zserver_frontend_url_list.split(","))

  suite = makeSuite(test_suite=args.test_suite,
                    node_quantity=args.node_quantity,
                    revision=revision,
                    db_list=args.db_list,
                    zserver_address_list=args.zserver_address_list,
                    zserver_frontend_url_list=args.zserver_frontend_url_list,
                    bt5_path=args.bt5_path,
                    firefox_bin=args.firefox_bin,
                    xvfb_bin=args.xvfb_bin)
  test_result = master.createTestResult(revision, suite.getTestList(),
    args.test_node_title, suite.allow_restart, test_suite_title,
    args.project_title)
  if test_result is not None:
    assert revision == test_result.revision, (revision, test_result.revision)
    while suite.acquire():
      test = test_result.start(suite.running.keys())
      if test is not None:
        suite.start(test.name, lambda status_dict, __test=test:
          __test.stop(**status_dict))
      elif not suite.running:
        break
