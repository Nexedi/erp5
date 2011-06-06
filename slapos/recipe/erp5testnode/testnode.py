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
  supervisord_pid_file = os.path.join(config['instance_root'], 'var', 'run',
        'supervisord.pid')
  subprocess.check_call([config['git_binary'],
                "config", "--global", "http.sslVerify", "false"])
  previous_revision = None

  run_software = True
  # Write our own software.cfg to use the local repository
  custom_profile_path = os.path.join(config['working_directory'], 'software.cfg')
  config['custom_profile_path'] = custom_profile_path
  vcs_repository_list = config['vcs_repository_list']
  profile_content = None
  assert len(vcs_repository_list), "we must have at least one repository"
  for vcs_repository in vcs_repository_list:
    url = vcs_repository['url']
    buildout_section_id = vcs_repository.get('buildout_section_id', None)
    repository_id = buildout_section_id or \
                                  url.split('/')[-1].split('.')[0]
    repository_path = os.path.join(config['working_directory'],repository_id)
    vcs_repository['repository_id'] = repository_id
    vcs_repository['repository_path'] = repository_path
    if profile_content is None:
      profile_content = """
[buildout]
extends = %(software_config_path)s
""" %  {'software_config_path': os.path.join(repository_path,
                                          config['profile_path'])}
    if not(buildout_section_id is None):
      profile_content += """
[%(buildout_section_id)s]
repository = %(repository_path)s
branch = %(branch)s
""" %  {'buildout_section_id': buildout_section_id,
        'repository_path' : repository_path,
        'branch' : vcs_repository.get('branch','')}

  custom_profile = open(custom_profile_path, 'w')
  custom_profile.write(profile_content)
  custom_profile.close()
  config['repository_path'] = repository_path
  sys.path.append(repository_path)
  test_suite_title = config['test_suite_title'] or config['test_suite']

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
        full_revision_list = []
        # Make sure we have local repository
        for vcs_repository in vcs_repository_list:
          repository_path = vcs_repository['repository_path']
          repository_id = vcs_repository['repository_id']
          if not os.path.exists(repository_path):
            parameter_list = [config['git_binary'], 'clone',
                              vcs_repository['url']]
            if vcs_repository.get('branch') is not None:
              parameter_list.extend(['-b',vcs_repository.get('branch')])
            parameter_list.append(repository_path)
            subprocess.check_call(parameter_list)
          # Make sure we have local repository
          updater = Updater(repository_path, git_binary=config['git_binary'])
          updater.checkout()
          revision = "-".join(updater.getRevision())
          full_revision_list.append('%s=%s' % (repository_id, revision))
        revision = ','.join(full_revision_list)
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
            config['test_suite'], revision, [],
            False, test_suite_title,
            config['test_node_title'], config['project_title'])
        print "testnode, test_result : %r" % (test_result,)
        if test_result:
          test_result_path, test_revision = test_result
          if revision != test_revision:
            for i, repository_revision in enumerate(test_revision.split(',')):
              vcs_repository = vcs_repository_list[i]
              repository_path = vcs_repository['repository_path']
              # other testnodes on other boxes are already ready to test another
              # revision
              updater = Updater(repository_path, git_binary=config['git_binary'],
                                revision=repository_revision.split('-')[1])
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
              test_result_path, status_dict, config['test_node_title'])
            retry_software = True
            continue

          # create instances, it should take some seconds only
          slapos_controler.runComputerPartition(config,
                  process_group_pid_set=process_group_pid_set)

          # update repositories downloaded by buildout. Later we should get
          # from master a list of repositories

          # The section below seems useless since we override buildout
          # configuration to use local checkouts
          #repository_path_list = glob(os.path.join(config['software_root'],
                                  #'*', 'parts', 'git_repository', '*'))
          #assert len(repository_path_list) >= 0
          #for repository_path in repository_path_list:
            #updater = Updater(repository_path, git_binary=config['git_binary'])
            #updater.checkout()
            #if os.path.split(repository_path)[-1] == repository_name:
              ## redo checkout with good revision, the previous one is used
              ## to pull last code
              #updater = Updater(repository_path, git_binary=config['git_binary'],
                                #revision=revision)
              #updater.checkout()

          partition_path = os.path.join(config['instance_root'],
                                        config['partition_reference'])
          run_test_suite_path = os.path.join(partition_path, 'bin',
                                            'runTestSuite')
          if not os.path.exists(run_test_suite_path):
            raise ValueError('No %r provided' % run_test_suite_path)

          run_test_suite_revision = revision
          if isinstance(revision, tuple):
            revision = ','.join(revision)
          # Deal with Shebang size limitation
          file_object = open(run_test_suite_path, 'r')
          line = file_object.readline()
          file_object.close()
          invocation_list = []
          if line[:2] == '#!':
            invocation_list = line[2:].split()
          invocation_list.extend([run_test_suite_path,
                                  '--test_suite', config['test_suite'],
                                  '--revision', revision,
                                  '--node_quantity', config['node_quantity'],
                                  '--master_url', config['test_suite_master_url']])
          run_test_suite = subprocess.Popen(invocation_list)
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

