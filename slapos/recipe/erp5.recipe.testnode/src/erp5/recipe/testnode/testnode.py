from xml_marshaller import xml_marshaller
import os, xmlrpclib, time, imp
from glob import glob
import signal
import slapos.slap
import subprocess
import sys
import socket
import pprint
from SlapOSControler import SlapOSControler


class SubprocessError(EnvironmentError):
  def __init__(self, status_dict):
    self.status_dict = status_dict
  def __getattr__(self, name):
    return self.status_dict[name]
  def __str__(self):
    return 'Error %i' % self.status_code


from Updater import Updater

process_group_pid_set = set()
process_pid_file_list = []
process_command_list = []
def sigterm_handler(signal, frame):
  for pgpid in process_group_pid_set:
    try:
      os.killpg(pgpid, signal.SIGTERM)
    except:
      pass
  for pid_file in process_pid_file_list:
    try:
      os.kill(int(open(pid_file).read().strip()), signal.SIGTERM)
    except:
      pass
  for p in process_command_list:
    try:
      subprocess.call(p)
    except:
      pass
  sys.exit(1)

signal.signal(signal.SIGTERM, sigterm_handler)

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

slapos_controler = None

def run(args):
  config = args[0]
  slapgrid = None
  branch = config.get('branch', None)
  supervisord_pid_file = os.path.join(config['instance_root'], 'var', 'run',
        'supervisord.pid')
  subprocess.check_call([config['git_binary'],
                "config", "--global", "http.sslVerify", "false"])
  previous_revision = None
  run_software = True
  # find what will be the path of the repository
  repository_name = config['vcs_repository'].split('/')[-1].split('.')[0]
  repository_path = os.path.join(config['working_directory'],repository_name)
  config['repository_path'] = repository_path
  sys.path.append(repository_path)

  # Write our own software.cfg to use the local repository
  custom_profile_path = os.path.join(config['working_directory'], 'software.cfg')
  config['custom_profile_path'] = custom_profile_path
  
  # create a profile in order to use the repository we already have
  custom_profile = open(custom_profile_path, 'w')
  profile_content = """
[buildout]
extends = %(software_config_path)s

[%(repository_name)s]
repository = %(repository_path)s
""" %     {'software_config_path': os.path.join(repository_path,
                                          config['profile_path']),
    'repository_name': repository_name,
    'repository_path' : repository_path}
  if branch is not None:
    profile_content += "\nbranch = %s" % branch
  custom_profile.write(profile_content)
  custom_profile.close()
  retry_software = False
  try:
    while True:
      # kill processes from previous loop if any
      try:
        for pgpid in process_group_pid_set:
          try:
            os.killpg(pgpid, signal.SIGTERM)
          except:
            pass
        process_group_pid_set.clear()
        # Make sure we have local repository
        if not os.path.exists(repository_path):
          parameter_list = [config['git_binary'], 'clone',
                            config['vcs_repository']]
          if branch is not None:
            parameter_list.extend(['-b',branch])
          parameter_list.append(repository_path)
          subprocess.check_call(parameter_list)
          # XXX this looks like to not wait the end of the command
        # Make sure we have local repository
        updater = Updater(repository_path, git_binary=config['git_binary'])
        updater.checkout()
        revision = updater.getRevision()
        if previous_revision == revision:
          time.sleep(120)
          if not(retry_software):
            continue
        retry_software = False
        previous_revision = revision

        print config
        portal_url = config['test_suite_master_url']
        test_result_path = None
        test_result = (test_result_path, revision)
        if portal_url:
          if portal_url[-1] != '/':
            portal_url += '/'
          portal = xmlrpclib.ServerProxy("%s%s" %
                      (portal_url, 'portal_task_distribution'),
                      allow_none=1)
          master = portal.portal_task_distribution
          assert master.getProtocolRevision() == 1
          test_result = safeRpcCall(master.createTestResult,
            config['test_suite_name'], revision, [],
            False, config['test_suite_title'])
        print "testnode, test_result : %r" % (test_result,)
        if test_result:
          test_result_path, test_revision = test_result
          if revision != test_revision:
            # other testnodes on other boxes are already ready to test another
            # revision
            updater = Updater(repository_path, git_binary=config['git_binary'],
                              revision=test_revision)
            updater.checkout()

          # Now prepare the installation of SlapOS
          slapos_controler = SlapOSControler(config,
            process_group_pid_set=process_group_pid_set)
          # this should be always true later, but it is too slow for now
          status_dict = slapos_controler.runSoftwareRelease(config,
            environment=config['environment'],
            process_group_pid_set=process_group_pid_set,
            )
          if status_dict['status_code'] != 0:
            safeRpcCall(master.reportTaskFailure,
              test_result_path, status_dict, config['test_suite_title'])
            retry_software = True
            continue

          # create instances, it should take some seconds only
          slapos_controler.runComputerPartition(config,
                  process_group_pid_set=process_group_pid_set)

          # update repositories downloaded by buildout. Later we should get
          # from master a list of repositories
          repository_path_list = glob(os.path.join(config['software_root'],
                                  '*', 'parts', 'git_repository', '*'))
          assert len(repository_path_list) >= 0
          for repository_path in repository_path_list:
            updater = Updater(repository_path, git_binary=config['git_binary'])
            updater.checkout()
            if os.path.split(repository_path)[-1] == repository_name:
              # redo checkout with good revision, the previous one is used
              # to pull last code
              updater = Updater(repository_path, git_binary=config['git_binary'],
                                revision=revision)
              updater.checkout()
            # calling dist/externals is only there for backward compatibility,
            # the code will be removed soon
            if os.path.exists(os.path.join(repository_path, 'dist/externals.py')):
              process = subprocess.Popen(['dist/externals.py'],
                        cwd=repository_path)
              process.wait()

          partition_path = os.path.join(config['instance_root'],
                                        config['partition_reference'])
          run_test_suite_path = os.path.join(partition_path, 'bin',
                                            'runTestSuite')
          if not os.path.exists(run_test_suite_path):
            raise ValueError('No %r provided' % run_test_suite_path)

          run_test_suite_revision = revision
          if isinstance(revision, tuple):
            revision = ','.join(revision)
          run_test_suite = subprocess.Popen([run_test_suite_path,
                          '--test_suite', config['test_suite_name'],
                          '--revision', revision,
                          '--node_quantity', config['node_quantity'],
                          '--master_url', config['test_suite_master_url'],
                          ], )
          process_group_pid_set.add(run_test_suite.pid)
          run_test_suite.wait()
          process_group_pid_set.remove(run_test_suite.pid)
      except SubprocessError:
        time.sleep(120)
        continue

  finally:
    # Nice way to kill *everything* generated by run process -- process
    # groups working only in POSIX compilant systems
    # Exceptions are swallowed during cleanup phase
    print "going to kill %r" % (process_group_pid_set,)
    for pgpid in process_group_pid_set:
      try:
        os.killpg(pgpid, signal.SIGTERM)
      except:
        pass
    try:
      if os.path.exists(supervisord_pid_file):
        os.kill(int(open(supervisord_pid_file).read().strip()), signal.SIGTERM)
    except:
      pass

