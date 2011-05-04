import os
import sys
def runUnitTest(args):
  env = os.environ.copy()
  d = args[0]
  env['OPENSSL_BINARY'] = d['openssl_binary']
  env['TEST_CA_PATH'] = d['test_ca_path']
  env['PATH'] = ':'.join([d['prepend_path']] + os.environ['PATH'].split(':'))
  env['INSTANCE_HOME'] = d['instance_home']
  env['REAL_INSTANCE_HOME'] = d['instance_home']
  os.execve(d['call_list'][0], d['call_list'] + sys.argv[1:], env)
