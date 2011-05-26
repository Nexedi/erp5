import os
import sys
def runTestSuite(args):
  env = os.environ.copy()
  d = args[0]
  env['OPENSSL_BINARY'] = d['openssl_binary']
  env['TEST_CA_PATH'] = d['test_ca_path']
  env['PATH'] = ':'.join([d['prepend_path']] + os.environ['PATH'].split(':'))
  env['INSTANCE_HOME'] = d['instance_home']
  env['REAL_INSTANCE_HOME'] = d['instance_home']
  # Deal with Shebang size limitation
  executable_filepath = d['call_list'][0]
  file_object = open(executable_filepath, 'r')
  line = file_object.readline()
  file_object.close()
  argument_list = []
  if line[:2] == '#!':
    executable_filepath = line[2:].strip()
    argument_list.append(executable_filepath)
  argument_list.extend(d['call_list'])
  argument_list.extend(sys.argv[1:])
  argument_list.append(env)
  os.execle(executable_filepath, *argument_list)
